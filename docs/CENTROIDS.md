# What Are Centroids?

Think of a centroid as the **average taste** of a group of coffees.

You have five cups labeled "authority bias." You taste each one — they taste of entitlement, of wanting the "right answer," of expecting deference. The centroid is the **average of those five tastes**. It's the center point of that bias category.

Now a new cup arrives. You don't know what it is. You taste it and ask: *is this closer to the authority average, or closer to the confirmation-bias average, or the sunk-cost average?*

**That's all a centroid is.** A center point in embedding space.

## Why the Prototype's Centroids Were Broken

The research code had fake float arrays like `[0.12, -0.45, 0.67]`. They looked like embeddings but were **made-up numbers**. That meant the classifier was doing arithmetic on fiction.

## How We Fix It

1. Pull a real embedding model (e.g., `nomic-embed-text`).
2. Write 5–10 example phrases for each bias category.
3. Ask Ollama to embed each phrase → you get real vectors (arrays of ~768 numbers).
4. Average those vectors → that's your real centroid.
5. Save it in `centroids/bias-centroids.json`.
6. From then on, the classifier uses **measured** centers, not guessed ones.

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

## How Many Do We Need?

Start with **6–8 bias categories**. Ten examples each. One run. ~5 minutes of generation. Then the classifier is grounded.

If you want to add new biases later, you generate new centroids and drop them in the file. Nothing else changes.
