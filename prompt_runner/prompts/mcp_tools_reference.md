# HoloMem MCP Tool Reference
Generated from the bridge catalog to reflect current MCP exposure.

| MCP Tool | Server Method | Required Args | Optional Args | Description | Examples |
| --- | --- | --- | --- | --- | --- |
| `holomem_adviseRetrieval` | `holomem.adviseRetrieval` | `N`:integer | `namespace`:null or string<br>`platform`:null or string<br>`target_latency`:null or string | Recommend exact vs ANN+candidates based on N (dataset size). | — |
| `holomem_advise_retrieval` | `holomem.adviseRetrieval` | `N`:integer | `namespace`:null or string<br>`platform`:null or string<br>`target_latency`:null or string | Recommend exact vs ANN+candidates based on N (dataset size). | — |
| `holomem_aggregate` | `holomem.aggregate` | `group_by`:object<br>`metrics`:object | `having`:null or object<br>`namespace`:null or string | Aggregate simple metrics (e.g., COUNT) over cohorts. | flat_group_by={"group_by": {"kind": "fn"}, "metrics": {"cnt_total": {"op": "COUNT_TOTAL"}}}; canonical_group_by={"group_by": {"has": {"kind": "fn"}}, "metrics": {"cnt": {"op": "COUNT"}}} |
| `holomem_aggregate_metrics` | `holomem.aggregate` | `group_by`:object<br>`metrics`:object | `having`:null or object<br>`namespace`:null or string | Aggregate simple metrics (e.g., COUNT) over cohorts. | flat_group_by={"group_by": {"kind": "fn"}, "metrics": {"cnt_total": {"op": "COUNT_TOTAL"}}}; canonical_group_by={"group_by": {"has": {"kind": "fn"}}, "metrics": {"cnt": {"op": "COUNT"}}} |
| `holomem_batchIngest` | `holomem.batchIngest` | `artifacts`:array | `error_threshold`:number<br>`namespace`:null or string<br>`on_error`:string<br>`provenance`:object<br>`txn`:null or string | Batch ingest artifacts with on_error policy; for simple property ingests (not parsing code). | — |
| `holomem_batchRemember` | `holomem.batchRemember` | `concepts`:array | `namespace`:null or string<br>`provenance`:object<br>`transaction_mode`:string<br>`txn`:null or string | Batch assertion of properties/relations (transactional modes). | — |
| `holomem_batchReplace` | `holomem.batchReplace` | `items`:array | `namespace`:null or string<br>`provenance`:object<br>`transaction_mode`:string<br>`txn`:null or string | Batch replace properties across items (transactional modes). | — |
| `holomem_beginTransaction` | `holomem.beginTransaction` | — | `isolation`:string<br>`namespace`:null or string | Begin a transaction (snapshot isolation). | — |
| `holomem_begin_transaction` | `holomem.beginTransaction` | — | `isolation`:string<br>`namespace`:null or string | Begin a transaction (snapshot isolation). | — |
| `holomem_checkpoint` | `holomem.checkpoint` | — | — | Create a snapshot of the current graph (id + evidence). | — |
| `holomem_collect_garbage` | `holomem.gc` | — | `dry_run`:boolean<br>`namespace`:null or string<br>`older_than`:null or string<br>`pattern`:null or string<br>`remove_unreferenced`:boolean | Garbage collection: pattern‑based candidates; support dry_run. | — |
| `holomem_commit` | `holomem.commit` | `txn`:string | `namespace`:null or string | Commit a transaction; return index versions. | — |
| `holomem_commit_transaction` | `holomem.commit` | `txn`:string | `namespace`:null or string | Commit a transaction; return index versions. | — |
| `holomem_compare_concepts` | `holomem.contrast` | `probe`:object<br>`candidates`:array | `lens`:string<br>`score_mode`:string | Explain ranking via feature deltas (probe vs candidates); supports lens. | — |
| `holomem_configure` | `holomem.configure` | `config`:object | — | Update server configuration (some options require restart). | — |
| `holomem_confirmHypothesis` | `holomem.confirmHypothesis` | `ids`:array | — | Confirm (materialize) hypothesis claims. | — |
| `holomem_confirm_hypothesis` | `holomem.confirmHypothesis` | `ids`:array | — | Confirm (materialize) hypothesis claims. | — |
| `holomem_contrast` | `holomem.contrast` | `probe`:object<br>`candidates`:array | `lens`:string<br>`score_mode`:string | Explain ranking via feature deltas (probe vs candidates); supports lens. | — |
| `holomem_copyToNamespace` | `holomem.copyToNamespace` | `from`:string<br>`to`:string | `filter`:null or object | Copy concepts from one namespace to another. | — |
| `holomem_copy_to_namespace` | `holomem.copyToNamespace` | `from`:string<br>`to`:string | `filter`:null or object | Copy concepts from one namespace to another. | — |
| `holomem_costEstimate` | `holomem.costEstimate` | `method`:string | `namespace`:null or string<br>`params`:object | Advisory cost estimate for an operation’s payload size. | — |
| `holomem_counterexample` | `holomem.counterexample` | `invariant`:object | `lens`:null or string<br>`max_depth`:integer or null | Find a minimal counterexample for a single invariant. | — |
| `holomem_createNamespace` | `holomem.createNamespace` | `name`:string | — | Create (initialize) a namespace. | — |
| `holomem_create_checkpoint` | `holomem.checkpoint` | — | — | Create a snapshot of the current graph (id + evidence). | — |
| `holomem_create_hypothesis` | `holomem.hypothesize` | `claims`:array | — | Add hypothesis claims (not materialized). | — |
| `holomem_create_namespace` | `holomem.createNamespace` | `name`:string | — | Create (initialize) a namespace. | — |
| `holomem_create_plan` | `holomem.plan` | `steps`:array | `namespace`:null or string | Materialize a plan as nodes with depends_on edges from high‑level steps. | — |
| `holomem_crossNamespaceSearch` | `holomem.crossNamespaceSearch` | `namespaces`:array<br>`text`:string | `topk`:integer or null | Search across multiple namespaces (NL). | — |
| `holomem_deleteNamespace` | `holomem.deleteNamespace` | `name`:string | — | Delete namespace graph + sidecars. | — |
| `holomem_delete_namespace` | `holomem.deleteNamespace` | `name`:string | — | Delete namespace graph + sidecars. | — |
| `holomem_describe` | `holomem.describe` | — | `include_values`:boolean<br>`kind`:string<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`role`:null or string | Describe roles, relations, policies, and capabilities. | — |
| `holomem_describeNamespace` | `holomem.describeNamespace` | `name`:string | — | Summarize a namespace (counts). | — |
| `holomem_describe_capabilities` | `holomem.describe` | — | `include_values`:boolean<br>`kind`:string<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`role`:null or string | Describe roles, relations, policies, and capabilities. | — |
| `holomem_describe_namespace` | `holomem.describeNamespace` | `name`:string | — | Summarize a namespace (counts). | — |
| `holomem_diagnose` | `holomem.diagnose` | — | — | Scan system and indexes for potential issues (advisory). | — |
| `holomem_diagnose_system` | `holomem.diagnose` | — | — | Scan system and indexes for potential issues (advisory). | — |
| `holomem_diffImpact` | `holomem.diffImpact` | `from_version`:string<br>`to_version`:string | `lens`:null or string<br>`namespace`:null or string | Compute change impact between snapshots (added/removed edges, impacted nodes). | — |
| `holomem_diffNamespaces` | `holomem.diffNamespaces` | `from`:string<br>`to`:string | — | Compare two namespaces (added/removed/changed). | — |
| `holomem_diff_impact` | `holomem.diffImpact` | `from_version`:string<br>`to_version`:string | `lens`:null or string<br>`namespace`:null or string | Compute change impact between snapshots (added/removed edges, impacted nodes). | — |
| `holomem_diff_namespaces` | `holomem.diffNamespaces` | `from`:string<br>`to`:string | — | Compare two namespaces (added/removed/changed). | — |
| `holomem_estimate_cost` | `holomem.costEstimate` | `method`:string | `namespace`:null or string<br>`params`:object | Advisory cost estimate for an operation’s payload size. | — |
| `holomem_execute_in_namespace` | `holomem.withNamespace` | `name`:string<br>`operation`:object | `fallback`:array or null<br>`policy`:null or string | Execute a nested tools/call inside a namespace view. | — |
| `holomem_expand_neighborhood` | `holomem.sliceContext` | `from`:array | `goal`:object<br>`lens`:string<br>`max_nodes`:integer<br>`page_size`:integer<br>`page_token`:string | Deterministic BFS‑LEX neighborhood from nodes; defaults lens=aliases; supports pagination. | — |
| `holomem_explore_counterfactual` | `holomem.whatIf` | `concept_name`:string | `change`:object<br>`dry_run`:boolean or null<br>`explain`:boolean or null<br>`include_performance`:boolean or null<br>`namespace`:null or string<br>`trace_depth`:integer | Create a counterfactual concept and analyze impacts (what‑if). | — |
| `holomem_find` | `holomem.find` | — | `explain`:boolean or null or object<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`query`:object<br>`score_mode`:null or string<br>`strict`:boolean or null<br>`topk`:integer | Structured find by has/is_a with topk/pagination. | — |
| `holomem_findRelevant` | `holomem.findRelevant` | `probe`:object | `explain`:boolean or null<br>`min_overlap`:null or object<br>`mode`:null or string<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`score_mode`:null or string<br>`topk`:integer | Semantic search by probe or concept name. | — |
| `holomem_find_by_properties` | `holomem.findBy` | — | `has`:null or object<br>`is_a`:null or object<br>`namespace`:null or string<br>`strict`:boolean or null<br>`topk`:integer or null | Structured find with minimal inputs (has/is_a). | — |
| `holomem_find_by_query` | `holomem.find` | — | `explain`:boolean or null or object<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`query`:object<br>`score_mode`:null or string<br>`strict`:boolean or null<br>`topk`:integer | Structured find by has/is_a with topk/pagination. | — |
| `holomem_find_counterexample` | `holomem.counterexample` | `invariant`:object | `lens`:null or string<br>`max_depth`:integer or null | Find a minimal counterexample for a single invariant. | — |
| `holomem_find_paths` | `holomem.queryPath` | — | `edge_filter`:array or null or object<br>`explain`:boolean or null<br>`from`:array<br>`lens`:null or string<br>`max_depth`:integer<br>`mode`:null or string<br>`namespace`:null or string<br>`namespaces`:array or null<br>`not_through`:array or null<br>`page_size`:integer<br>`page_token`:null or string<br>`policy`:null or string<br>`to`:array | Simple paths with cycle pruning, edge_filter, explain diagnostics, and certificates; defaults lens=aliases. | manual={"from": ["pkg.mod.Caller.fn"], "to": ["pkg2.auth.Service.login"], "lens": "aliases", "max_depth": 6}; auto_intent={"from": ["pkg.tasks.TaskManager"], "to": ["pkg.auth.AuthService"], "lens": "aliases", "mode": "auto", "max_depth": 6} |
| `holomem_find_similar_concepts` | `holomem.findRelevant` | `probe`:object | `explain`:boolean or null<br>`min_overlap`:null or object<br>`mode`:null or string<br>`namespace`:null or string<br>`page_size`:integer<br>`page_token`:null or string<br>`score_mode`:null or string<br>`topk`:integer | Semantic search by probe or concept name. | — |
| `holomem_forget` | `holomem.forget` | `concept_name`:string | `namespace`:null or string<br>`property`:null or object<br>`provenance`:object<br>`relation`:null or object<br>`txn`:null or string | Remove a property or relation (policy‑aware neutralization). | — |
| `holomem_forgetHypothesis` | `holomem.forgetHypothesis` | `ids`:array | — | Forget hypothesis claims. | — |
| `holomem_gc` | `holomem.gc` | — | `dry_run`:boolean<br>`namespace`:null or string<br>`older_than`:null or string<br>`pattern`:null or string<br>`remove_unreferenced`:boolean | Garbage collection: pattern‑based candidates; support dry_run. | — |
| `holomem_get` | `holomem.get` | `concept_name`:string | `namespace`:null or string | Get full details for a concept (properties + asserted relations). | — |
| `holomem_getConfig` | `holomem.getConfig` | — | — | Return current configuration. | — |
| `holomem_getCurrentNamespace` | `holomem.getCurrentNamespace` | — | — | Return the current namespace. | — |
| `holomem_get_capabilities` | `holomem.capabilities` | — | — | Return client-usable capability hints and defaults. | — |
| `holomem_get_class_methods` | `holomem.listMethods` | `class`:string | `enrich`:boolean or null<br>`namespace`:null or string<br>`strict`:boolean or null<br>`topk`:integer or null | List methods for a class. | — |
| `holomem_get_code_slice` | `holomem.codeSlice` | `symbol`:string | `enrich`:boolean or null<br>`lens`:null or string<br>`namespace`:null or string | Focused structural slice for a symbol (bounded). | — |
| `holomem_get_concept` | `holomem.get` | `concept_name`:string | `namespace`:null or string | Get full details for a concept (properties + asserted relations). | — |
| `holomem_get_config` | `holomem.getConfig` | — | — | Return current configuration. | — |
| `holomem_get_current_namespace` | `holomem.getCurrentNamespace` | — | — | Return the current namespace. | — |
| `holomem_get_docstring` | `holomem.getDocstring` | `symbol`:string | `full`:boolean or null<br>`namespace`:null or string | Return docstring summary/full (bounded). | — |
| `holomem_get_function_callers` | `holomem.listCallers` | — | — | holomem_get_function_callers | — |
| `holomem_get_function_calls` | `holomem.listCalls` | `symbol`:string | `lens`:null or string<br>`namespace`:null or string | List direct callees for a symbol. | — |
| `holomem_get_implementation_anchors` | `holomem.getImplementation` | `symbol`:string | `max_excerpt`:integer or null<br>`namespace`:null or string | Return implementation anchors; optional excerpt (bounded). | example={"symbol": "pkg.mod:Class.method", "max_excerpt": 320} |
| `holomem_get_many_symbols` | `holomem.batchGet` | `symbols`:array | `namespace`:null or string<br>`page_size`:integer or null<br>`page_token`:null or string | Batch compact summaries for symbols (paginated). | — |
| `holomem_get_neighborhood` | `holomem.contextGraph` | `node`:string | `enrich`:boolean or null<br>`lens`:null or string<br>`max_nodes`:integer or null<br>`namespace`:null or string | Neighborhood graph around a node (bounded BFS-LEX). | — |
| `holomem_get_program_slice` | `holomem.sliceProgram` | `symbol`:string | `bounds`:object<br>`lens`:string | Structural slice around a symbol (symbol=module[.Class][.method]); include certificates. | — |
| `holomem_get_quickstart_overview` | `holomem.quickStart` | — | `namespace`:null or string<br>`topk`:integer or null | Quick overview of a namespace (summary + entry points). | — |
| `holomem_get_role_budget` | `holomem.roleBudget` | `role`:string | `cap`:integer or null<br>`namespace`:null or string<br>`warn`:boolean or null | Report strict_N for a role; warn near caps. | — |
| `holomem_get_signature` | `holomem.getSignature` | `symbol`:string | `namespace`:null or string | Return signature metadata for a symbol (bounded). | — |
| `holomem_get_system_stats` | `holomem.statistics` | — | `filter`:null or object<br>`kind`:null or string<br>`namespace`:null or string | Graph/performance/health statistics. | — |
| `holomem_get_tests_map` | `holomem.testsMap` | `node`:string | `coverage_uri`:string | Map a code node to tests (reads tested_by property/relation); optional coverage provenance. | — |
| `holomem_get_versions` | `holomem.version` | — | — | Return bridge/server versions and protocol version. | — |
| `holomem_hypothesize` | `holomem.hypothesize` | `claims`:array | — | Add hypothesis claims (not materialized). | — |
| `holomem_ingestPython` | `holomem.ingestPython` | `module`:string<br>`code`:string | `enrich`:boolean or null<br>`namespace`:null or string<br>`provenance`:object<br>`txn`:null or string | Parse a Python module into code concepts and explicit calls (per‑file, idempotent). | — |
| `holomem_ingest_bundle` | `holomem.projectBundle` | `kind`:string<br>`payload`:object | `namespace`:null or string<br>`provenance`:object | Deterministically ingest a pre‑parsed bundle (ConceptDTOs + triples) for brownfield DTOs. | — |
| `holomem_ingest_many_artifacts` | `holomem.batchIngest` | `artifacts`:array | `error_threshold`:number<br>`namespace`:null or string<br>`on_error`:string<br>`provenance`:object<br>`txn`:null or string | Batch ingest artifacts with on_error policy; for simple property ingests (not parsing code). | — |
| `holomem_ingest_python_code` | `holomem.ingestPython` | `module`:string<br>`code`:string | `enrich`:boolean or null<br>`namespace`:null or string<br>`provenance`:object<br>`txn`:null or string | Parse a Python module into code concepts and explicit calls (per‑file, idempotent). | — |
| `holomem_linkSymbols` | `holomem.linkSymbols` | `canonical_name`:string<br>`symbols`:array | `namespace`:null or string | Link language symbols to a canonical concept. | — |
| `holomem_link_symbols` | `holomem.linkSymbols` | `canonical_name`:string<br>`symbols`:array | `namespace`:null or string | Link language symbols to a canonical concept. | — |
| `holomem_listNamespaces` | `holomem.listNamespaces` | — | — | List available namespaces persisted on disk. | — |
| `holomem_list_classes` | `holomem.listClasses` | — | `enrich`:boolean or null<br>`module`:null or string<br>`namespace`:null or string<br>`topk`:integer or null | List classes under an optional module prefix. | — |
| `holomem_list_enums` | `holomem.listEnums` | — | `module`:null or string<br>`namespace`:null or string<br>`topk`:integer or null | List enums under an optional module prefix. | — |
| `holomem_list_namespaces` | `holomem.listNamespaces` | — | — | List available namespaces persisted on disk. | — |
| `holomem_moveToNamespace` | `holomem.moveToNamespace` | `from`:string<br>`to`:string | `filter`:null or object | Move concepts from one namespace to another. | — |
| `holomem_move_to_namespace` | `holomem.moveToNamespace` | `from`:string<br>`to`:string | `filter`:null or object | Move concepts from one namespace to another. | — |
| `holomem_plan` | `holomem.plan` | `steps`:array | `namespace`:null or string | Materialize a plan as nodes with depends_on edges from high‑level steps. | — |
| `holomem_profile` | `holomem.profile` | — | `capture`:array or null<br>`duration`:integer | Capture profiling/tracing signals (bounded duration). | — |
| `holomem_profile_system` | `holomem.profile` | — | `capture`:array or null<br>`duration`:integer | Capture profiling/tracing signals (bounded duration). | — |
| `holomem_promoteNamespace` | `holomem.promoteNamespace` | `name`:string | — | Promote from default to a named namespace (enable persistence). | example={"name": "alpha"} |
| `holomem_promote_namespace` | `holomem.promoteNamespace` | `name`:string | — | Promote from default to a named namespace (enable persistence). | example={"name": "alpha"} |
| `holomem_prune_checkpoints` | `holomem.pruneCheckpoints` | `name`:string<br>`keep`:integer | — | Keep the last N checkpoints (lexicographic, latest first). | example={"name": "alpha", "keep": 10} |
| `holomem_queryPath` | `holomem.queryPath` | — | `edge_filter`:array or null or object<br>`explain`:boolean or null<br>`from`:array<br>`lens`:null or string<br>`max_depth`:integer<br>`mode`:null or string<br>`namespace`:null or string<br>`namespaces`:array or null<br>`not_through`:array or null<br>`page_size`:integer<br>`page_token`:null or string<br>`policy`:null or string<br>`to`:array | Simple paths with cycle pruning, edge_filter, explain diagnostics, and certificates; defaults lens=aliases. | manual={"from": ["pkg.mod.Caller.fn"], "to": ["pkg2.auth.Service.login"], "lens": "aliases", "max_depth": 6}; auto_intent={"from": ["pkg.tasks.TaskManager"], "to": ["pkg.auth.AuthService"], "lens": "aliases", "mode": "auto", "max_depth": 6} |
| `holomem_rebuild` | `holomem.rebuild` | — | `namespace`:null or string<br>`roles`:array or null | Rebuild reverse index versions for roles (accepts roles list). | — |
| `holomem_rebuild_indexes` | `holomem.rebuild` | — | `namespace`:null or string<br>`roles`:array or null | Rebuild reverse index versions for roles (accepts roles list). | — |
| `holomem_record_session` | `holomem.sessionRecord` | `method`:string | `evidence`:object<br>`params`:object | Record an auditable session payload (ledger id). | — |
| `holomem_remember` | `holomem.remember` | `concept_name`:string | `namespace`:null or string<br>`properties`:object<br>`provenance`:object<br>`relations`:array or array or object<br>`txn`:null or string | Assert/merge properties for a concept (idempotent). | — |
| `holomem_remove_concept` | `holomem.forget` | `concept_name`:string | `namespace`:null or string<br>`property`:null or object<br>`provenance`:object<br>`relation`:null or object<br>`txn`:null or string | Remove a property or relation (policy‑aware neutralization). | — |
| `holomem_remove_hypothesis` | `holomem.forgetHypothesis` | `ids`:array | — | Forget hypothesis claims. | — |
| `holomem_replace` | `holomem.replace` | `concept_name`:string | `namespace`:null or string<br>`new`:object<br>`previous`:object<br>`provenance`:object<br>`txn`:null or string | Atomic replace of properties (set to exactly), with validation. | — |
| `holomem_replace_concept` | `holomem.replace` | `concept_name`:string | `namespace`:null or string<br>`new`:object<br>`previous`:object<br>`provenance`:object<br>`txn`:null or string | Atomic replace of properties (set to exactly), with validation. | — |
| `holomem_replace_many_concepts` | `holomem.batchReplace` | `items`:array | `namespace`:null or string<br>`provenance`:object<br>`transaction_mode`:string<br>`txn`:null or string | Batch replace properties across items (transactional modes). | — |
| `holomem_resolveSymbol` | `holomem.resolveSymbol` | `language`:string<br>`fqname`:string | `namespace`:null or string | Resolve a language symbol (e.g., python fqname) to canonical identity. | — |
| `holomem_resolve_symbol` | `holomem.resolveSymbol` | `language`:string<br>`fqname`:string | `namespace`:null or string | Resolve a language symbol (e.g., python fqname) to canonical identity. | — |
| `holomem_restore_checkpoint` | `holomem.restore_checkpoint` | `id`:null or string | `namespace`:null or string | Restore a previously saved checkpoint (destructive). | example={"id": "20240918-120102-alpha-v12"} |
| `holomem_rollback` | `holomem.rollback` | `txn`:string | `namespace`:null or string | Rollback a transaction. | — |
| `holomem_rollback_transaction` | `holomem.rollback` | `txn`:string | `namespace`:null or string | Rollback a transaction. | — |
| `holomem_search_across_namespaces` | `holomem.crossNamespaceSearch` | `namespaces`:array<br>`text`:string | `topk`:integer or null | Search across multiple namespaces (NL). | — |
| `holomem_search_by_text` | `holomem.search` | `text`:string | `namespace`:null or string<br>`topk`:integer or null | Natural-language search across names + metadata (bounded). | — |
| `holomem_sessionRecord` | `holomem.sessionRecord` | `method`:string | `evidence`:object<br>`params`:object | Record an auditable session payload (ledger id). | — |
| `holomem_shortest_paths_between` | `holomem.pathBetween` | — | `edge_filter`:array or null<br>`explain`:boolean or null<br>`from`:array<br>`lens`:null or string<br>`max_depth`:integer<br>`namespace`:null or string<br>`namespaces`:array or null<br>`policy`:null or string<br>`to`:array | Bounded shortest paths (namespaced union/first_hit). | example={"from": ["A"], "to": ["B"], "max_depth": 3, "namespaces": ["main", "dev"], "policy": "union"} |
| `holomem_statistics` | `holomem.statistics` | — | `filter`:null or object<br>`kind`:null or string<br>`namespace`:null or string | Graph/performance/health statistics. | — |
| `holomem_store_concept` | `holomem.remember` | `concept_name`:string | `namespace`:null or string<br>`properties`:object<br>`provenance`:object<br>`relations`:array or array or object<br>`txn`:null or string | Assert/merge properties for a concept (idempotent). | — |
| `holomem_store_many_concepts` | `holomem.batchRemember` | `concepts`:array | `namespace`:null or string<br>`provenance`:object<br>`transaction_mode`:string<br>`txn`:null or string | Batch assertion of properties/relations (transactional modes). | — |
| `holomem_summarizeAnchored` | `holomem.summarizeAnchored` | `nodes`:array | `lens`:string<br>`max_tokens`:integer | Summarize anchored nodes; supports lens and token bounds. | — |
| `holomem_summarize_anchored` | `holomem.summarizeAnchored` | `nodes`:array | `lens`:string<br>`max_tokens`:integer | Summarize anchored nodes; supports lens and token bounds. | — |
| `holomem_switch_to_namespace` | `holomem.useNamespace` | `name`:string | `create_if_missing`:boolean or null | Switch to a namespace for isolation (session-scoped). | example={"name": "projA"} |
| `holomem_synthesize` | `holomem.synthesize` | `concept_name`:string | `dry_run`:boolean or null<br>`explain`:boolean or null<br>`goal`:object<br>`namespace`:null or string | Steer a concept toward a goal state (advisory, evidence‑first). | — |
| `holomem_synthesize_concept` | `holomem.synthesize` | `concept_name`:string | `dry_run`:boolean or null<br>`explain`:boolean or null<br>`goal`:object<br>`namespace`:null or string | Steer a concept toward a goal state (advisory, evidence‑first). | — |
| `holomem_testsMap` | `holomem.testsMap` | `node`:string | `coverage_uri`:string | Map a code node to tests (reads tested_by property/relation); optional coverage provenance. | — |
| `holomem_update_config` | `holomem.configure` | `config`:object | — | Update server configuration (some options require restart). | — |
| `holomem_useNamespace` | `holomem.useNamespace` | `name`:string | `create_if_missing`:boolean or null | Switch to a namespace for isolation (session-scoped). | example={"name": "projA"} |
| `holomem_validate_graph` | `holomem.validateGraph` | — | — | holomem_validate_graph | example={"max_samples": 10} |
| `holomem_validate_invariants` | `holomem.verifyInvariants` | `rules`:array | `lens`:string | Verify bounded invariants; return minimal counterexamples. | — |
| `holomem_verify` | `holomem.verify` | — | — | Verify index consistency; return versions and issues. | — |
| `holomem_verifyInvariants` | `holomem.verifyInvariants` | `rules`:array | `lens`:string | Verify bounded invariants; return minimal counterexamples. | — |
| `holomem_verifyNamespace` | `holomem.verifyNamespace` | `name`:string | — | Verify manifest/digest integrity for a namespace. | example={"name": "alpha"} |
| `holomem_verify_indexes` | `holomem.verify` | — | — | Verify index consistency; return versions and issues. | — |
| `holomem_verify_namespace` | `holomem.verifyNamespace` | `name`:string | — | Verify manifest/digest integrity for a namespace. | example={"name": "alpha"} |
| `holomem_whatIf` | `holomem.whatIf` | `concept_name`:string | `change`:object<br>`dry_run`:boolean or null<br>`explain`:boolean or null<br>`include_performance`:boolean or null<br>`namespace`:null or string<br>`trace_depth`:integer | Create a counterfactual concept and analyze impacts (what‑if). | — |
| `overlays_list` | `overlays.list` | — | — | List registered overlays with kind and precedence. | — |
| `resources_batch_read` | `resources.batch_read` | — | `uris`:array | Batch read resource URIs; order preserving. | — |
