# Revenue scope firewall and v6 train diagnostic — checkpoint

- Time: 2026-11-16 10:04 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User explicitly skipped P3 reviewer. Reviewer status is **SKIPPED**; P3 remains **NOT VERIFIED / NOT PASSED**. No reviewer annotations or ≥81% acceptance metric are claimed. P1/P2 were not repeated; Docker is out of scope.

## Code and tests

- `understanding.py` now structures common percentage share and best-sales-day questions, and fails closed on explicit named-product, product breakdown, payment/channel breakdown, counter-service (`tại quầy`) and product mentions using `món`, `tiền bán <name>`, or `bán <name> được` forms. Average-revenue queries no longer fall through to total revenue.
- `metrics.py` emits internal `invalid_unit` when the user explicitly requests a non-VND unit from scalar revenue; output JSONL schema is unchanged.
- Regression coverage includes synthetic Vietnamese paraphrases plus false-positive guards for generic revenue and product ranking.
- Focused tests after latest code changes: `PYTHONPATH=src python -m unittest tests.test_understanding tests.test_pipeline tests.test_query_schema -v` — 48 passed.
- Complete suite after latest code changes: `PYTHONPATH=src python -m unittest discover -s tests -v` — 115 run, 112 passed, 3 Git-dependent hygiene tests skipped, exit 0.
- Current code hashes: `understanding.py` `854EEFE34968F2FE243B3ED19124C7FFF996EAABDF302CF9C56F44CE04914CFC`; `metrics.py` `9D0A251038B5F37F398C66D9298BE5A799AD34FFCF87248787F28DE61E0EAAAF`; `test_understanding.py` `D0968F9A727E56B86E35C819318C7C5EB22B2BCC9686E09A035A2D13BB63EB64`; `test_pipeline.py` `D11D9630697962C81CFD88188212B734E1EA205009C58493A10C9D0506BFFF9F`.

## Frozen train evaluation (v6b)

- Prediction generation completed for 3,000 questions / 30 businesses, `answer_labels_accessed=false`; evaluator validated freeze, input, and code hashes before reading train labels.
- Evaluation report: `work/evaluation/p6-train-replay-v6b-revenue-firewall-2026-11-16/evaluation_report.json`.
- Metrics: PA `-0.001`; 43 correct, 46 wrong, 2,911 abstentions; coverage `2.97%`; answered accuracy `48.31%`; false-answer rate `51.69%`; correctly abstained on 70/70 unanswerable cases; p50 1 ms / p95 44 ms; runtime errors `{}`.
- Versus v5, PA improved by `0.004`, wrong answers fell by 14, and correct answers fell by 2; coverage fell by 0.53 percentage points. This is an **in-sample train diagnostic**, not independent acceptance and far below the playbook gates.
- v6b wrong answers by intent: revenue 39, cancellation_rate 2, order_count 2, quantity 2, sales_ranking 1. All 39 revenue errors were numeric answers to numeric references; 24 were biz_127, 10 biz_129, 5 biz_116. The v6b QuerySpecs had empty filter/dimension slots for these cases.
- Read-only schema inspection showed distinct amount semantics: biz_116 line-level `Thành tiền` with states including `không giao được` and `đang vận chuyển`; biz_127 order-level `Tổng đơn` alongside `Khách trả`/`Còn nợ`; biz_129 `Phải thu` alongside `Thanh toán`/`Dư nợ`. No revenue aggregation/source change is justified until the source/official business definition and join/reconciliation contract is established. No values, IDs, or business-specific rules were added.

### Frozen provenance

- Prediction SHA-256: `298265c704715fc3bbd871309c805f0516eed861317c5952529bf03da784ca58`.
- Trace SHA-256: `6f8c7f91103bef9ce013297ee47af18ad49cd90638e5951e9937affaf193b14e`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Code manifest SHA-256 at v6b generation: `c9d0590321d4bfe03ab84631516bbe6cff5e6f8f501da83422a5c575602c00c3`.
- Freeze manifest SHA-256: `0403e606dfa629f1ee4452b3fcab6e0919904356e034ba6e93d9e71b368499b0`.
- Training answer archive SHA-256, recorded by evaluator: `0b5fe9d13edf5fae306bda9cafaf699c06b639846c8e1d9e41c39a86d1160b3d`.
- The latest generic product/channel filter regression changes were added **after** v6b evaluation; therefore v6b metrics do not measure the exact current source snapshot (current `understanding.py` hash above). Do not present it as a score for current code.
- Earlier incomplete attempt `work/evaluation/p6-train-replay-v6-revenue-firewall-2026-11-16` is preserved untouched and was not evaluated.

## Safety and next work

- Train labels were used only after the checksum-verified freeze for evaluation and error categorization. Public Test was not used. No label-specific rules, answer values, question IDs, or per-business logic were added.
- No source archives, official checkout, Git history, Docker artifacts, or other branches were modified; no commit or push occurred.
- Next: continue P4/P7 work using documented source contracts and synthetic fixtures. Establish revenue amount/status/denominator/join semantics before changing aggregate behavior. Keep P3, P4, P5, P6 in progress/not accepted until their measurable rubric gates have evidence.
