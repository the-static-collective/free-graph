# RELAY-001 — sixth organ: SIA → Free Graph

## Actual seam

The new \`scripts/relay001_sia.py\` is a **read-only native Free Graph consumer** of SIA's fifth-organ \`sia/relay-index/v0\` and local content-addressed vault.

A graph of historical facts *about the observed relay* is not a graph that owns the source projects.

It uses the unmodified Free Graph v0 contract:
- \`project-source\` records for seven SIA objects (the index, song observation, and five stage records);
- one song artifact, five stage artifacts, five observed project-name nodes, and 34 **proposed** candidate nodes;
- \`connects\` for named associations and invitations;
- \`descends-from\` only for the four explicit SIA parent pointers;
- **no** \`constitutes\`, owner-local authority, or automatically resolved world heads;
- native \`rehash_packet(..., stamp=True)\`, \`validate_packet\`, \`neighbors\`, and \`merge_packets\`.

The importer independently re-hashes all six SIA vault objects, compares SIA's five stage records to its index, checks exact parent order, and rejects candidate status inflation. With \`--packet-root\`, it **also** checks bytes for all 12 linked JSON evidence files and the original local MP3. This is **not** a re-execution of GHoT nor a fresh cryptographic verification of the reLATTE crossing. Those already belong to their project-owned interfaces.

### Native use with your fifth-organ archive

\`\`\`sh
python3 scripts/relay001_sia.py \
  --sia-index /path/to/five-organ/fifth-organ/relay-index.json \
  --vault /path/to/five-organ/fifth-organ/vault \
  --packet-root /path/to/five-organ \
  --output /tmp/relay001.free-graph.json

python3 scripts/fg.py validate /tmp/relay001.free-graph.json
python3 scripts/fg.py neighbors /tmp/relay001.free-graph.json '<NODE_ID>' --depth 1
\`\`\`

Without \`--packet-root\`, the SIA vault and index are independently validated, but the graph's \`exact_local_evidence_bytes_checked\` remains \`false\`.

The graph exports **digests and local coordinates, not the MP3**, physical paths, private receiver state, or external URL live status. Source metadata is marked restricted and pointer-only.

## What the graph can answer

- What evidence/relay event immediately preceded this event?
- Which observed stages relate to this exact source song?
- Which 34 project doors remain **proposed**, not executed?
- What happens when a lens moves to a 1-hop or 2-hop neighborhood?
- Does merging projections enlarge evidence coverage while leaving authority unchanged?

## Strict limits

- SIA's \`verification.verified\` flag is historical testimony. Free Graph cannot promote that into independent truth.
- The four recorded \`descends-from\` links are SIA parent-pointer lineage, not necessarily physical causal history.
- A named project in the index is not proof of current repository head, operating capability, signed owner authority or availability.
- \`RECEIVED_HELD\` remains observed reLATTE disposition. A graph edge is **not** receiver admission.
- No original media is committed to this public branch. CI uses synthetic content.

### Frontier

Once reviewed, webZ can *display* this bounded graph packet as a navigable evidence doorway. Reading/traversal is always separate from executing another organ.
