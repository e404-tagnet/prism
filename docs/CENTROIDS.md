# What Are Centroids?

Think of a centroid as the **average taste** of a group of coffees.

You have five cups labeled "authority bias." You taste each one — they taste of entitlement, of wanting the "right answer," of expecting deference. The centroid is the **average of those five tastes**. It's the center point of that bias category.

Now a new cup arrives. You don't know what it is. You taste it and ask: *is this closer to the authority average, or closer to the confirmation-bias average, or the sunk-cost average?*

**That's all a centroid is.** A center point in embedding space.

## Why the Prototype's Centroids Were Broken

The research code had fake float arrays like `[0.12, -0.45, 0.67]`. They looked like embeddings but were **made-up numbers**. That meant the classifier was doing arithmetic on fiction.

## How We Fixed It

1. ✅ Pulled `nomic-embed-text` via Ollama.
2. ✅ Wrote 10 example phrases for each of 8 bias categories.
3. ✅ Embedded each phrase via Ollama → real vectors (768 numbers each).
4. ✅ Averaged those vectors → real centroids.
5. ✅ Saved them in `centroids/bias-centroids.json`.
6. ✅ The embedding classifier now uses **measured** centers, not guessed ones.

## Visual

```
Embedding Space (768 dimensions)

     ● authority centroid
    / \
   ●   ●     ● confirmation centroid
  /     \
 ●       ●

new message ●  ← which centroid is it closest to?
```

## How Many Do We Have?

**8 bias categories**, 10 examples each, generated in one run (~5 minutes). The classifier is grounded.

If you want to add new biases later, generate new centroids and drop them in the file. Nothing else changes.
