"""
Prompt templates for narrative structure extraction
"""

# 论文类型识别 Prompt
CLASSIFY_PAPER_TYPE_PROMPT = """You are an expert in academic paper classification. Analyze the following paper and classify it into ONE of these 6 types:

1. **reduced_form**: Reduced-Form / Applied Micro Paper (Labor, Development, Public Economics, Health)
   - Goal: Causal Inference (finding X's effect on Y)
   - Keywords: Difference-in-Differences (DiD), Regression Discontinuity (RD), Instrumental Variables (IV), RCT

2. **structural**: Structural Paper (Macroeconomics, IO, Trade)
   - Goal: Building mathematical models for "what-if" scenarios
   - Keywords: Calibration, GMM, SMM, Counterfactuals, DSGE

3. **pure_theory**: Pure Theory Paper (Micro Theory, Game Theory, Mechanism Design)
   - Goal: Establishing logical truths and equilibrium properties
   - Keywords: Nash Equilibrium, Bayesian Perfect Equilibrium, Theorems, Proofs

4. **experimental**: Experimental Paper (Behavioral Economics, Experimental Finance)
   - Goal: Testing human behavior in controlled settings
   - Keywords: Lab experiment, Field experiment, Treatment, Control group, RCT

5. **econometric**: Econometric / Methodological Paper
   - Goal: Creating new statistical tools
   - Keywords: Estimator, Asymptotic properties, Monte Carlo simulations

6. **descriptive**: Descriptive / Measurement / Stylized Facts Paper
   - Goal: Documenting trends, correlations, and facts
   - Keywords: Data construction, Stylized facts, Decomposition

---
PAPER CONTENT:
{paper_content}
---

Respond with ONLY the type code (one of: reduced_form, structural, pure_theory, experimental, econometric, descriptive).
"""

# Layer 1 通用核心提取 Prompt
EXTRACT_LAYER1_PROMPT = """You are an expert in academic paper analysis. Extract the narrative structure from the following paper.

Extract these fields (respond in JSON format):

1. **research_question**: The precise question the authors are trying to answer
2. **mechanism**: How does X affect Y? The logical chain or channel
3. **headline_result**: The one-sentence summary of the main finding
4. **policy_implications**: Actionable advice for policymakers (if any, otherwise "Not explicitly stated")
5. **contribution**: How is this different from existing literature? What's the "delta"?
6. **hook_motivation**: Why does this matter? What motivates the research?
7. **context_setting**: Where and when does this apply? (e.g., setting, time period, domain)

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object containing these 7 fields. Be concise but precise. If a field cannot be determined from the paper, use "Not explicitly stated".
"""

# Layer 2 各类型特定字段提取 Prompts
EXTRACT_LAYER2_PROMPTS = {
    "reduced_form": """You are an expert in empirical economics. Extract the methodological details from this Reduced-Form / Applied Micro paper.

Extract these fields (respond in JSON format):

1. **identification_strategy**: The causal identification method (DiD, RD, IV, RCT, etc.)
2. **treatment_shock**: What is the exogenous event or treatment?
3. **control_group**: Who/what is the comparison group?
4. **data_sources**: What data sources are used?
5. **validity_checks**: What validity checks are performed? (parallel trends, balance tests, etc.)
6. **clustering**: At what level are standard errors clustered?
7. **robustness_checks**: What robustness checks are mentioned?

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
""",

    "structural": """You are an expert in structural economics. Extract the methodological details from this Structural paper.

Extract these fields (respond in JSON format):

1. **model_environment**: Describe the model setup
   - agents: Who is in the model?
   - time_horizon: Infinite horizon, OLG, finite period?
   - market_structure: Perfect competition, monopolistic, oligopoly?
   - key_frictions: What frictions drive the results?
2. **estimation_method**: How are parameters estimated? (Calibration, GMM, SMM, MLE)
3. **moments_targeted**: What data moments does the model target?
4. **key_parameters**: What are the key parameters? (preferences, technology, etc.)
5. **counterfactuals**: What hypothetical scenarios are analyzed?
6. **model_fit**: How well does the model fit non-targeted moments?

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
""",

    "pure_theory": """You are an expert in economic theory. Extract the methodological details from this Pure Theory paper.

Extract these fields (respond in JSON format):

1. **setup_primitives**: Describe the theoretical setup
   - information_structure: Complete vs incomplete information
   - action_space: Continuous vs discrete
   - players: Who are the agents/players?
2. **solution_concept**: What equilibrium concept is used? (Nash, Bayesian Perfect, etc.)
3. **main_theorems**: List the main theorems/propositions and their content
4. **proof_methods**: What proof techniques are used? (induction, fixed point, etc.)
5. **existence_uniqueness**: Results on existence and uniqueness of equilibrium
6. **comparative_statics**: How does equilibrium change with parameters?

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
""",

    "experimental": """You are an expert in experimental economics. Extract the methodological details from this Experimental paper.

Extract these fields (respond in JSON format):

1. **experimental_design**: Describe the experiment design
   - subject_pool: Who are the subjects? (students, professionals, etc.)
   - sample_size: Number of participants
   - incentivization: How were subjects incentivized?
2. **treatments**: List the treatment conditions
3. **control_condition**: What is the control/baseline condition?
4. **pre_analysis_plan**: Was a pre-analysis plan registered?
5. **elicitation_method**: How were beliefs/preferences measured?
6. **main_behavioral_findings**: Key findings about behavior

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
""",

    "econometric": """You are an expert in econometrics. Extract the methodological details from this Econometric/Methodological paper.

Extract these fields (respond in JSON format):

1. **estimator_proposed**: Describe the new estimator or method proposed
2. **asymptotic_properties**: Consistency, efficiency, bias properties
3. **finite_sample_properties**: Small sample behavior
4. **monte_carlo_simulations**: Description of simulation studies
5. **empirical_application**: Any empirical applications shown?
6. **software_package**: Is a software package provided? (Stata, R, Python)

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
""",

    "descriptive": """You are an expert in empirical economics. Extract the methodological details from this Descriptive/Measurement paper.

Extract these fields (respond in JSON format):

1. **data_construction**: How was the dataset built? What sources?
2. **stylized_facts**: What are the main patterns/facts documented?
3. **decomposition_method**: How are trends decomposed? (within vs between, extensive vs intensive)
4. **correlational_evidence**: What correlations are documented?
5. **measurement_challenges**: What measurement issues are addressed?
6. **time_period_coverage**: What time period does the data cover?

---
PAPER CONTENT:
{paper_content}
---

Respond ONLY with a valid JSON object. If a field cannot be determined, use "Not explicitly stated".
"""
}

# 论文类型中文名称映射
PAPER_TYPE_NAMES = {
    "reduced_form": "Reduced-Form / Applied Micro (实证微观)",
    "structural": "Structural (结构模型)",
    "pure_theory": "Pure Theory (纯理论)",
    "experimental": "Experimental (实验)",
    "econometric": "Econometric / Methodological (计量方法论)",
    "descriptive": "Descriptive / Measurement (描述性/测量)"
}

# Layer 2 字段中文名称映射
LAYER2_FIELD_NAMES = {
    "reduced_form": {
        "identification_strategy": "识别策略",
        "treatment_shock": "处理/冲击",
        "control_group": "控制组",
        "data_sources": "数据来源",
        "validity_checks": "有效性检验",
        "clustering": "聚类层级",
        "robustness_checks": "稳健性检验"
    },
    "structural": {
        "model_environment": "模型环境",
        "estimation_method": "估计方法",
        "moments_targeted": "目标矩",
        "key_parameters": "关键参数",
        "counterfactuals": "反事实分析",
        "model_fit": "模型拟合"
    },
    "pure_theory": {
        "setup_primitives": "设置/原语",
        "solution_concept": "解概念",
        "main_theorems": "主要定理",
        "proof_methods": "证明方法",
        "existence_uniqueness": "存在性与唯一性",
        "comparative_statics": "比较静态"
    },
    "experimental": {
        "experimental_design": "实验设计",
        "treatments": "处理组",
        "control_condition": "控制条件",
        "pre_analysis_plan": "预分析计划",
        "elicitation_method": "诱导方法",
        "main_behavioral_findings": "主要行为发现"
    },
    "econometric": {
        "estimator_proposed": "提出的估计量",
        "asymptotic_properties": "渐近性质",
        "finite_sample_properties": "有限样本性质",
        "monte_carlo_simulations": "蒙特卡洛模拟",
        "empirical_application": "实证应用",
        "software_package": "软件包"
    },
    "descriptive": {
        "data_construction": "数据构建",
        "stylized_facts": "典型事实",
        "decomposition_method": "分解方法",
        "correlational_evidence": "相关性证据",
        "measurement_challenges": "测量挑战",
        "time_period_coverage": "时间覆盖"
    }
}

LAYER1_FIELD_NAMES = {
    "research_question": "研究问题",
    "mechanism": "机制/渠道",
    "headline_result": "主要结果",
    "policy_implications": "政策含义",
    "contribution": "贡献",
    "hook_motivation": "动机",
    "context_setting": "背景/适用范围"
}
