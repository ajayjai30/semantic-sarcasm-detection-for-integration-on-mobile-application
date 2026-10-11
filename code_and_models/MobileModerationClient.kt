package com.moderation.mobile

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import kotlin.math.exp

/**
 * Result data class returned by MobileModerationClient.
 *
 * @property isBlocked Whether the input message was flagged and blocked.
 * @property stage The evaluation stage that determined the outcome (1 = slur hard block, 2 = classifier).
 * @property reason Diagnostic explanation (matched slur token, hostility probability, or clean status).
 * @property probability Toxicity / sarcasm probability (1.0 for Stage 1 hard block, [0.0..1.0] for Stage 2).
 * @property latencyUs Total end-to-end evaluation latency in microseconds (µs).
 */
data class ModerationResult(
    val isBlocked: Boolean,
    val stage: Int,
    val reason: String,
    val probability: Float,
    val latencyUs: Long
)

/**
 * High-performance, zero-ML-dependency embedded moderation client for mobile devices.
 * Implements a two-stage filter:
 *   - Stage 1: Deterministic Trie with word boundary checks (< 25 µs)
 *   - Stage 2: Folded linear sarcasm & mock-praise classifier (< 250 µs)
 */
class MobileModerationClient private constructor(
    private val stage1Trie: TrieNode,
    private val stage2Intercept: Float,
    private val stage2Weights: Map<String, Float>,
    private val threshold: Float = DEFAULT_THRESHOLD
) {

    companion object {
        const val DEFAULT_THRESHOLD = 0.50f

        /**
         * Initializes client from the static bundle JSON string (`moderation_mobile_bundle.json`).
         * Uses Android's built-in `org.json.JSONObject` (zero external dependencies).
         */
        fun fromJson(jsonString: String, threshold: Float = DEFAULT_THRESHOLD): MobileModerationClient {
            val rootObj = JSONObject(jsonString)

            // 1. Parse Stage 1 exact slurs
            val slursArray = rootObj.getJSONArray("stage1_exact_slurs")
            val slurList = ArrayList<String>(slursArray.length())
            for (i in 0 until slursArray.length()) {
                slurList.add(slursArray.getString(i))
            }

            // 2. Parse Stage 2 intercept & weights
            val intercept = rootObj.getDouble("stage2_intercept").toFloat()
            val weightsObj = rootObj.getJSONObject("stage2_weights")
            val weightsMap = HashMap<String, Float>(weightsObj.length())
            val keys = weightsObj.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                weightsMap[key] = weightsObj.getDouble(key).toFloat()
            }

            return fromBundle(slurList, intercept, weightsMap, threshold)
        }

        /**
         * Initializes client directly from pre-parsed collections.
         */
        fun fromBundle(
            slurs: List<String>,
            intercept: Float,
            weights: Map<String, Float>,
            threshold: Float = DEFAULT_THRESHOLD
        ): MobileModerationClient {
            val root = TrieNode()
            for (slur in slurs) {
                val clean = slur.trim().lowercase()
                if (clean.isEmpty()) continue
                var curr = root
                for (ch in clean) {
                    curr = curr.children.getOrPut(ch) { TrieNode() }
                }
                curr.isEndOfWord = true
                curr.matchedWord = clean
            }

            return MobileModerationClient(
                stage1Trie = root,
                stage2Intercept = intercept,
                stage2Weights = weights,
                threshold = threshold
            )
        }
    }

    /**
     * Synchronous on-thread evaluation. Guaranteed runtime typically < 100-250 µs.
     */
    fun evaluate(text: String): ModerationResult {
        val startNs = System.nanoTime()
        val cleanText = text.trim()

        if (cleanText.isEmpty()) {
            val elapsedUs = (System.nanoTime() - startNs) / 1_000
            return ModerationResult(
                isBlocked = false,
                stage = 1,
                reason = "EMPTY_INPUT",
                probability = 0.0f,
                latencyUs = elapsedUs
            )
        }

        val textLower = cleanText.lowercase()

        // ============================================================
        // STAGE 1: Deterministic Trie with Strict Word Boundary Checks
        // ============================================================
        val matchedSlur = scanStage1(textLower)
        if (matchedSlur != null) {
            val elapsedUs = (System.nanoTime() - startNs) / 1_000
            return ModerationResult(
                isBlocked = true,
                stage = 1,
                reason = "STAGE_1_EXPLICIT_SLUR: $matchedSlur",
                probability = 1.0f,
                latencyUs = elapsedUs
            )
        }

        // ============================================================
        // STAGE 2: Sub-Word Folded Weight Linear Classifier
        // ============================================================
        var linearScore = stage2Intercept

        // Word (1, 2)-grams
        val wordTokens = extractWordTokens(textLower)
        val wordNgrams = HashSet<String>()
        for (i in wordTokens.indices) {
            wordNgrams.add(wordTokens[i])
            if (i + 1 < wordTokens.size) {
                wordNgrams.add("${wordTokens[i]} ${wordTokens[i + 1]}")
            }
        }
        for (w in wordNgrams) {
            val weight = stage2Weights["w:$w"] ?: stage2Weights[w] ?: 0.0f
            linearScore += weight
        }

        // Character (3, 5)-grams
        val textLen = textLower.length
        val charNgrams = HashSet<String>()
        for (len in 3..5) {
            if (textLen >= len) {
                for (i in 0..textLen - len) {
                    charNgrams.add(textLower.substring(i, i + len))
                }
            }
        }
        for (c in charNgrams) {
            val weight = stage2Weights["c:$c"] ?: stage2Weights[c] ?: 0.0f
            linearScore += weight
        }

        // Sigmoid mapping: P = 1 / (1 + e^(-z)) with clamp against float overflow
        val clampedScore = linearScore.coerceIn(-50.0f, 50.0f)
        val prob = (1.0 / (1.0 + exp(-clampedScore.toDouble()))).toFloat()

        val isBlocked = prob >= threshold
        val reason = if (isBlocked) "STAGE_2_HOSTILITY_OR_SARCASM" else "CLEAN_CONVERSATION"
        val elapsedUs = (System.nanoTime() - startNs) / 1_000

        return ModerationResult(
            isBlocked = isBlocked,
            stage = 2,
            reason = reason,
            probability = prob,
            latencyUs = elapsedUs
        )
    }

    /**
     * Non-blocking asynchronous evaluation via Kotlin Coroutines.
     */
    suspend fun evaluateAsync(text: String): ModerationResult = withContext(Dispatchers.Default) {
        evaluate(text)
    }

    // ============================================================
    // INTERNAL HELPERS
    // ============================================================

    private fun scanStage1(text: String): String? {
        val n = text.length
        for (i in 0 until n) {
            // Optimization: Skip traversal if preceding character is alphanumeric/Tamil
            if (i > 0 && isWordChar(text[i - 1])) {
                continue
            }

            var curr: TrieNode? = stage1Trie
            for (j in i until n) {
                val ch = text[j]
                curr = curr?.children?.get(ch) ?: break

                if (curr.isEndOfWord) {
                    // Strict word boundary check at right flank
                    val isEndBoundary = (j + 1 >= n) || !isWordChar(text[j + 1])
                    if (isEndBoundary) {
                        return curr.matchedWord
                    }
                }
            }
        }
        return null
    }

    private fun extractWordTokens(text: String): List<String> {
        val tokens = ArrayList<String>()
        val sb = java.lang.StringBuilder()
        for (ch in text) {
            if (isWordChar(ch)) {
                sb.append(ch)
            } else {
                if (sb.length >= 2) {
                    tokens.add(sb.toString())
                }
                sb.setLength(0)
            }
        }
        if (sb.length >= 2) {
            tokens.add(sb.toString())
        }
        return tokens
    }

    private fun isWordChar(c: Char): Boolean {
        return c.isLetterOrDigit() || (c in '\u0B80'..'\u0BFF')
    }

    /**
     * Standard internal Trie node representation using native HashMap.
     */
    class TrieNode {
        val children: HashMap<Char, TrieNode> = HashMap()
        var isEndOfWord: Boolean = false
        var matchedWord: String? = null
    }
}

/**
 * Optional service wrapper for dependency injection frameworks (e.g. Dagger/Hilt).
 */
class MobileModerationService(private val client: MobileModerationClient) {
    fun checkMessage(text: String): ModerationResult = client.evaluate(text)
    suspend fun checkMessageAsync(text: String): ModerationResult = client.evaluateAsync(text)
}
