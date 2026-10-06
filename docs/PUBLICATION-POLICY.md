# Publication policy

[English](PUBLICATION-POLICY.md) | [简体中文](PUBLICATION-POLICY.zh-CN.md)

This repository is public. A private exporter applies the rules below. CI checks
the result. The rules have two parts: what we publish, and what we never publish.

## 1. Material that we publish

- Our reverse-engineered C source in `src/matched/`.
- Configuration data, symbol names, addresses, and function boundaries.
- Our own scripts in `tools/`.
- The progress report and the baseline in `progress/`.
- Our own documents in this repository.

## 2. Material that we never publish

- A game ROM, a game image, or the retail executable.
- A game asset, or a large part of the game text.
- A disassembly tree from `splat`, or an assembly listing that we copied.
- A full pseudo-C output from a decompiler.
- A Sony compiler, an SDK file, or a tool that Sony owns.
- Material from a third party without a licence.
- A key, a token, or a circumvention tool.

We publish a fact about the game only when it is our own measurement. Examples
are a function size, a symbol address, or a match result.

## 3. Report a problem

Open an issue if you find material in this repository that breaks section 2.
We treat that report as a blocker. We remove the material before any other work.

## 4. Note

- This policy applies to this public repository only.
- The private working repository is not public. It has no publication limit.
- You must own the game. This repository gives you no game data.
