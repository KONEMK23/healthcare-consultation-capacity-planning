# Planning Consultation Capacity Under Worried-Well Demand

**Student:** [[STUDENT_NAME]]
**Student ID:** [[STUDENT_ID]]
**Module:** MATH6186 Operational Research Case Study
**Facilitator:** Dr Bismark Singh
**Submission date:** 8 September 2026

## Abstract

An emerging outbreak can generate consultation requests from genuinely infected people and from worried-well people whose perceived risk motivates help-seeking despite their not being infected. This report asks how daily consultation capacity should change when worried-well behaviour, demand uncertainty, and shortage costs vary. A literature-derived four-compartment model generates synthetic early-outbreak trajectories. Coursework assumptions then translate infected and worried-well fractions into consultation demand, add mean-matched stochastic variation, and select a separate integer capacity for each day through a classical newsvendor rule. Capacity is optimized on 5,000 scenarios and evaluated on 10,000 independent scenarios. The experiments compare behavioural contact, uncertainty, shortage-cost, service-seeking, and initial-condition settings. Results show that behaviour changes both the timing and composition of pressure: more cautious interaction delays the infected peak but sustains worried-well pressure, whereas high contact brings a larger infected peak earlier. Capacity must therefore follow the joint demand curve rather than infections alone. Greater uncertainty increases expected mismatch cost, while a larger shortage penalty moves the policy above mean demand and makes optimization more valuable. Under balanced costs, the finite-sample comparison is slightly adverse rather than beneficial. These synthetic planning experiments demonstrate an operational connection, not an empirically calibrated clinical estimate.

## 1. Introduction

Healthcare consultation systems face a distinctive coordination problem during an emerging infectious-disease event. People with symptoms or infection risk may seek assessment, but fear and perceived exposure can also prompt demand from people who are not infected. The latter group is commonly described as the worried well. Its presence matters operationally because appointment, triage, telephone, testing, and clinical capacity can be consumed regardless of the eventual diagnostic category. A plan based only on the infected compartment may consequently miss an early and potentially substantial source of workload. Clinical discussion establishes the healthcare relevance of worried-well behaviour, while work on outbreak fear supplies a psychological rationale for treating perceived risk as dynamic rather than fixed [@chatterjee_2020] [@asmundson_taylor_2020].

The decision studied here is the number of pooled consultation slots to make available on each day of a 50-day early-outbreak horizon. Too little capacity leaves demand unmet and creates an underage consequence; too much capacity leaves resources unused and creates an overage consequence. Demand is uncertain, so choosing the deterministic mean is not generally optimal when those consequences differ. At the same time, demand is endogenous to behavioural dynamics: infected and worried-well fractions rise and fall at different times, and their relative contribution changes with contact behaviour. Capacity planning therefore requires a bridge from behavioural epidemiological structure to a stochastic operational decision.

The research question is: **How should daily consultation capacity change when worried-well behaviour, demand uncertainty, and shortage costs vary during an early outbreak?** The report answers this question through reproducible synthetic planning experiments. First, a literature-derived four-compartment ordinary differential equation system generates susceptible, infected, worried-well, and recovered fractions. Second, assumed service-seeking rates convert the infected and worried-well fractions into daily mean consultation demand for a synthetic population. Third, stochastic demand scenarios and a classical single-period newsvendor model produce integer daily capacities. Finally, out-of-sample comparisons assess behavioural, uncertainty, cost, service-seeking, and initial-condition sensitivity.

The scope is deliberately narrow. The generated trajectories are not empirical prevalence estimates, and the consultation model is not calibrated to a particular provider. Costs express planning priorities rather than monetary valuations. The contribution is instead methodological and operational: it shows how an explicitly represented worried-well process can alter the timing, scale, and uncertainty buffer of consultation capacity, while preserving a complete evidence trail from implemented equations and saved scenario outputs to each reported result.

## 2. Literature Review

### Worried-well behaviour as an operational phenomenon

The worried-well concept sits between psychological response and healthcare operations. Chatterjee et al. discuss its re-emergence during COVID-19 and establish why apparently healthy but concerned people can be relevant to healthcare systems [@chatterjee_2020]. For this report, the important inference is not that every concerned individual requests a consultation. It is that a non-infected population can generate service demand, so infection counts and consultation pressure need not coincide. A resource model that ignores that channel risks treating all requests as a direct consequence of infection. Equally, the cited article is a conceptual clinical discussion rather than an optimization study. It provides motivation for representing worried-well demand but supplies neither the capacity rule nor numerical service-seeking inputs used here.

Asmundson and Taylor place fear and anxiety within the context of an emerging outbreak, supporting the idea that perceived risk can influence behaviour [@asmundson_taylor_2020]. This perspective helps explain why worried-well prevalence can evolve alongside the infection process: concern may spread through social interaction and perceived exposure, then diminish as people leave the worried state. In operational terms, the psychological process can shift demand earlier than an infection-only workload model would suggest. However, the source does not provide a compartmental resource-planning model. It cannot by itself determine the magnitude of worried-well consultation requests, a stochastic demand distribution, or a capacity decision. Those elements remain explicit modelling choices in this project.

### Interacting behavioural and infection dynamics

Singh and Gromov provide the closest structural foundation for the present analysis. Their mathematical treatment defines a four-compartment worried-well model and behavioural regimes that connect infection and concern within one dynamic system [@singh_gromov_2025]. This is important because the two processes are not merely added after separate simulations. Susceptible people may enter an infected or worried-well state, interaction between infected and worried-well people can transfer pressure between states, and recovery or relaxation returns people through the system. The parameter alpha changes the interaction between infected and worried-well groups, allowing cautious, default, and high-contact regimes to be compared on a common basis.

The four-compartment structure also has a deeper modelling lineage. Blyuss and Kyrychko analyse a basic model of two interacting disease processes, providing the two-process foundation cited in the worried-well modelling work [@blyuss_kyrychko_2005]. That contribution supports the general logic of representing coupled spreading mechanisms rather than forcing all dynamics into a single infected compartment. Its limitation is decisive for the current research question: it concerns interacting transmission processes, not worried-well consultation demand or capacity. Accordingly, the present report uses it as conceptual background only. It is not treated as evidence for service probabilities, demand variability, or operational costs.

The Singh and Gromov framework makes behavioural scenario analysis possible, but it stops before the operational decision addressed here. Its synthetic early-outbreak dynamics do not estimate consultation capacity. A worried-well fraction is not identical to a request count, and a request count is not itself a capacity choice. Moving from the dynamic model to operations requires three additional specifications: how likely each compartment is to seek service, how realized demand varies around its conditional mean, and how shortage is valued relative to unused capacity. These specifications are recorded as coursework assumptions rather than attributed to the literature. This provenance separation is essential because it prevents a useful structural source from being misrepresented as empirical calibration.

### Outbreak resources and timing

Resource scarcity during outbreaks has been studied through other operational decisions. Singh and Rebennack examine whether scarce therapeutic resources should be released immediately or sequentially, connecting epidemic timing to resource allocation [@singh_rebennack_2026]. The relevance here is the general principle that when demand and health states vary over time, the timing of a resource decision matters. Daily consultation slots similarly need to follow changing pressure rather than being set from a horizon-wide average. Nevertheless, therapeutic release is a different decision from reserving consultation capacity. It involves allocation over time and scarcity of a treatment stock, whereas this project repeats a single-period capacity decision each day. The paper therefore motivates temporal operational reasoning but does not validate the newsvendor formulation, demand assumptions, or cost parameters used below.

This distinction prevents two resource questions from being conflated. A release policy asks when and to whom a finite stock should be deployed, potentially carrying resource availability between periods. The model in this report asks how many units of a pooled service to schedule for one day, with no carry-over of unused capacity. The daily decisions form a time-indexed sequence because the demand distribution changes, not because inventory is transferred across days. The implication is that the resulting capacity curve should be read as a set of repeated operating targets. It does not describe a stock-allocation trajectory or a multi-period scheduling programme. This scoped abstraction should be viewed alongside broader surge-capacity planning, which emphasizes scalable and flexible responses across facilities and communities when routine resources are exceeded [@hick_2004].

### Stochastic demand and the newsvendor connection

Once infected and worried-well states are translated into requests, realized workload remains uncertain. The classical newsvendor model is a natural starting point because it balances the expected consequence of capacity below demand against that of capacity above demand. Qin et al. review the newsvendor problem, its critical-fractile foundation, and major extensions [@qin_2011]. That foundation justifies a quantile-based decision when underage and overage costs are positive. If shortage is more consequential than unused capacity, the selected quantile lies above the median; if the two costs are balanced, the target approaches the median.

The review also makes clear that newsvendor research extends far beyond the simple form used here. The current project deliberately adopts one pooled resource, one uncertain demand quantity per day, linear mismatch costs, and a single-period decision. It does not model multiple service classes, substitution, queues, workforce shifts, appointment carry-over, or learning between days. Qin et al. therefore support the classical decision principle, not every contextual assumption. The costs, stochastic coefficient of variation, integerization procedure, and evaluation design remain project choices documented in the evidence record.

Stochastic epidemic modelling can instead introduce randomness within the state-transition process itself, for example through continuous-time Markov chains or stochastic differential equations [@allen_2017]. The present study adopts a narrower coursework extension: it retains the literature-derived deterministic compartment trajectories and places uncertainty in the downstream consultation-demand scenarios. This choice keeps the newsvendor input transparent while avoiding any claim that epidemiological parameter uncertainty has been estimated.

### Synthesis and gap

The literature supplies complementary pieces but not the complete decision chain. Worried-well and outbreak-anxiety research establishes why non-infected concern matters; interacting-process models provide a dynamic representation; outbreak-resource work emphasizes timing; and the newsvendor literature supplies a tractable stochastic capacity rule. None of these sources directly converts four-compartment worried-well trajectories into optimized daily consultation capacity. This report fills that modelling gap for a coursework case study by linking the components transparently.

The synthesis is intentionally critical. Literature-derived elements are limited to the four-compartment structure, behavioural alpha regimes, baseline rates and initial condition, plus the classical critical-fractile logic. The synthetic population size, consultation probabilities, coefficient of variation, mismatch costs, scenario counts, and sensitivity settings are coursework assumptions. As a result, the experiment can answer how capacity behaves *within the stated model* but cannot establish what a real provider should schedule without local estimation and a richer service representation.

## 3. Deterministic Worried-Well Model

The deterministic layer represents population fractions in four mutually exclusive compartments: susceptible \(S(t)\), genuinely infected \(I_P(t)\), worried-well \(I_W(t)\), and recovered \(R_P(t)\). The implemented system is:

[[EQUATION:compartment_system]]

The first equation removes susceptible people through infection-related contact and worried-well contact, while allowing recovered people to become susceptible and worried-well people to relax back to susceptibility. The second adds genuine infections generated through susceptible–infected contact and the alpha-scaled interaction between infected and worried-well people, then removes infected people through recovery. The third collects worried-well entry from susceptible interactions, subtracts alpha-scaled transfer associated with infected–worried interaction, and includes relaxation. The fourth balances recovery and loss of recovered status. Summing the four derivatives gives zero; the saved trajectories retain a total population fraction of one, which is the numerical conservation check.

The interaction terms give alpha a specific interpretation within the system. Raising alpha strengthens the transfer associated with encounters between infected and worried-well people: it contributes positively to the infected equation and negatively to the worried-well equation by the same amount. Alpha therefore changes composition without breaking conservation. The susceptible interaction terms separately generate infected and worried-well entry, while gamma parameters remove people from the active compartments. Delta allows recovered people to return to susceptibility. These mechanisms explain why a regime can bring infection forward while shortening the period in which worried-well prevalence remains large. They do not represent a causal estimate of any named public-health action.

The baseline parameters are adopted from Singh and Gromov’s structure and baseline scenario [@singh_gromov_2025]. They are \(\beta_P=0.74\), \(\beta_W=0.70\), \(\beta_{WP}=0.70\), \(\gamma_P=\gamma_W=1/14\), and \(\delta_P=1/240\). The initial state is \((0.98, 0.01, 0.01, 0)\), ordered as susceptible, infected, worried-well, and recovered. The behavioural multiplier takes \(\alpha=0.5\) for cautious contact, \(\alpha=1\) for the default regime, and \(\alpha=2\) for high contact. The model is integrated over 50 days and recorded daily.

[[PARAMETER_TABLE]]

The parameter table is also a provenance boundary. The compartment structure, alpha regimes, baseline rates, and baseline initial state are literature-derived model elements. By contrast, applying the fractions to a population of 100,000, translating compartments into service requests, and selecting uncertainty and cost settings are coursework assumptions. Alpha should therefore be read as a controlled behavioural scenario rather than an estimated intervention effect. Likewise, compartment fractions describe the internally generated system state, not measured prevalence. The deterministic model supplies the shape and composition of latent consultation pressure; the next section defines the operational demand mapping.

## 4. Stochastic Consultation Demand

For day \(t\), expected consultation demand combines the two request-generating compartments:

[[EQUATION:expected_demand]]

Here \(N\) is the synthetic population, \(p_P\) is the probability that an infected person seeks consultation, and \(p_W\) is the corresponding probability for a worried-well person. The baseline uses \(N=100{,}000\), \(p_P=1\), and \(p_W=0.5\). Thus every infected person contributes to conditional mean demand, while half of the worried-well compartment does so. These probabilities are explicit coursework inputs, not estimates from the cited clinical literature. Sensitivity analysis varies \(p_W\) while holding the structural trajectory fixed.

The conditional mean alone would imply perfectly known daily workload. To represent operational uncertainty, the implementation draws non-negative values from a lower-truncated normal distribution whose location is solved so that the post-truncation mean matches the required daily mean. The scale is linked to that mean through a coefficient of variation. Fractional draws are converted to non-negative integers by stochastic rounding, preserving the mean in expectation rather than mechanically rounding every scenario in the same direction.

Mean matching matters near the non-negative boundary. Simply truncating a conventional normal distribution at zero would lift its mean above the requested value, which would confound structural demand with an artefact of the distributional transformation. Solving for the pre-truncation location avoids that systematic shift. Stochastic integerization then translates continuous draws into count-valued requests without always rounding down or up. Zero conditional mean is handled directly as zero demand. Together, these choices make scenario averages target the demand equation while retaining non-negativity and integer units.

The baseline coefficient of variation is \(0.15\), with sensitivity settings \(0.05\) and \(0.30\). For each experimental configuration, 5,000 demand scenarios generated with seed 6186 form the optimization sample. A distinct set of 10,000 scenarios generated with seed 6187 forms the evaluation sample. Fixed seeds make comparisons reproducible and support common scenario conditions across policies. The distributional family and coefficient-of-variation values remain planning assumptions; they are not inferred from appointment or surveillance records.

Uncertainty is conditional and day-specific: the deterministic trajectory fixes the mean, then draws vary around it. The percentile band does not represent uncertainty about beta, alpha, the initial state, or the ODE solution; that would require an outer sampling layer. Daily capacity decisions also remain operationally independent.

## 5. Newsvendor Formulation

Let \(q_t\) be the non-negative integer consultation capacity selected for day \(t\), and let \(D_{ts}\) be demand in scenario \(s\). Underage cost \(c_u\) applies to each unit of demand above capacity, while overage cost \(c_o\) applies to each unused unit of capacity. For an in-sample set of size \(M\), the day-specific sample-average objective is:

[[EQUATION:sample_average_cost]]

The model chooses \(q_t\) separately for every day. Baseline costs are \(c_u=5\) and \(c_o=1\), expressing a stronger planning penalty for unmet demand than unused capacity. Cost sensitivity uses underage values \(1\), \(5\), and \(10\) while fixing overage at \(1\). These are dimensionless relative consequences and coursework assumptions; they are not monetary costs or empirically elicited preferences.

For the classical linear mismatch objective, the target demand quantile is determined by:

[[EQUATION:critical_fractile]]

The implementation computes this critical fractile in a numerically stable form and selects the corresponding in-sample integer order statistic. Under baseline costs, the target is above the centre of the demand distribution because shortage is more heavily penalized. Under balanced costs, it is the median. A mean-demand benchmark rounds each day’s conditional mean to the nearest integer, allowing the effect of asymmetric uncertainty-aware planning to be assessed out of sample.

The order-statistic rule is also a sample-average optimizer for the piecewise-linear loss. Candidate capacity increases trade one unit of expected shortage against one unit of expected unused capacity. At the critical fractile, the accumulated scenario probability below capacity is sufficient for the marginal overage consequence to balance the marginal underage consequence. Because realized demand is integer-valued, adjacent capacities can occasionally have very similar costs. The selected in-sample quantile is thus an operating target conditional on one generated sample, not a claim of a unique continuous optimum.

Both policies are evaluated on the same 10,000 scenarios for each experimental configuration. Daily expected cost is the scenario average of underage plus overage loss, and total cost is the sum across the 51 recorded days from day zero through day 50. This comparison isolates the capacity rule; neither policy changes the compartment trajectory or future demand. There is no queue, backlogging, or carry-over, so unmet requests and unused slots do not enter the following day’s state.

Out-of-sample evaluation reduces the risk of crediting a policy for adapting to random features of its optimization draw. Using identical evaluation scenarios for optimized and mean policies further makes the comparison paired: each rule faces the same daily demand realizations. The reported difference can still vary with the finite samples, especially when costs are balanced and the two rules select nearby capacities. For that reason, the sign and magnitude of every comparison are retained as generated.

## 6. Experimental Design

The experiment grid contains five groups chosen to answer distinct parts of the research question. First, the behaviour group varies \(\alpha\) across \(0.5\), \(1\), and \(2\) while retaining baseline demand uncertainty, costs, service probabilities, and initial state. This group shows how coupled infection and worried-well dynamics change both pressure and the daily capacity path. Second, the uncertainty group crosses those three behavioural regimes with coefficients of variation \(0.05\), \(0.15\), and \(0.30\), revealing how dispersion changes expected mismatch cost.

Third, the cost group fixes default behaviour and baseline uncertainty, then sets the underage-to-overage combinations to \(1{:}1\), \(5{:}1\), and \(10{:}1\). This isolates the effect of operational priorities on the critical fractile and the value of optimizing rather than planning at the mean. Fourth, service-seeking sensitivity sets worried-well consultation probability to \(0.25\), \(0.50\), \(0.75\), and \(1.00\). Fifth, initial-condition sensitivity compares the baseline infected and worried fractions with two asymmetric starts: infected \(0.01\) and worried-well \(0.001\), then infected \(0.001\) and worried-well \(0.01\). The susceptible fraction adjusts so that population is conserved.

Each configuration follows the same two-stage protocol. The 5,000 in-sample scenarios determine daily optimized capacity; the 10,000 out-of-sample scenarios estimate performance for both optimized and mean-demand policies. Seeds 6186 and 6187 separate decision fitting from evaluation while keeping the workflow exactly reproducible. Recorded measures include mean demand, demand percentiles, optimized capacity, expected shortage, unused capacity, shortage probability, and total mismatch cost.

Only the parameter named by an experiment group is varied from its baseline, apart from the deliberate alpha crossing in the uncertainty group. This controlled construction supports attribution within the model: differences between cost rows arise from costs, while differences between service-seeking rows arise from the demand mapping. It does not remove interactions that were not included in the grid, so conclusions should remain tied to the tested settings.

The design is comparative rather than inferential. It explores controlled scenarios and reports finite-sample expected performance within the implemented distribution. No confidence claim is made about a healthcare population. The figures provide qualitative readings, while numeric statements in the Results are linked to saved summary rows. This separation makes it possible to distinguish conclusions supported by generated evidence from assumptions that would require local validation before operational use.

## 7. Results

### 7.1 Behavioural regimes

Behaviour changes both the height and timing of the two active compartments. In the cautious regime, the infected fraction peaks at [[VALUE:behaviour_alpha_0.5|peak_infected|.3f]] on day [[VALUE:behaviour_alpha_0.5|peak_infected_day|.0f]], while the worried-well fraction peaks earlier at [[VALUE:behaviour_alpha_0.5|peak_worried|.3f]] on day [[VALUE:behaviour_alpha_0.5|peak_worried_day|.0f]]. Under default behaviour, the corresponding infected peak is [[VALUE:behaviour_alpha_1|peak_infected|.3f]] on day [[VALUE:behaviour_alpha_1|peak_infected_day|.0f]], and under high contact it is [[VALUE:behaviour_alpha_2|peak_infected|.3f]] on day [[VALUE:behaviour_alpha_2|peak_infected_day|.0f]]. The figure should be read horizontally as a timing comparison and vertically as a comparison of model fractions. Higher alpha brings a larger infected peak forward while compressing the worried-well episode; lower alpha delays infected pressure and leaves a more persistent worried-well contribution. These are deterministic scenario fractions, not measured prevalence.

[[FIGURE:figure_1_compartments.png|Compartment trajectories under cautious, default, and high-contact behaviour.|fig1]]

The worried-well-to-infected ratio clarifies why an infection-only staffing signal is incomplete. All three generated paths move above the reference value of one early in the horizon, meaning that the worried-well compartment temporarily exceeds the infected compartment. The cautious path remains above one longer and reaches the highest relative separation; the high-contact path crosses back sooner as infection accelerates. The ratio is useful for reading *composition*, not absolute workload: consultation pressure also depends on the synthetic population and different service-seeking probabilities. It is a conditional model ratio, not a measured ratio of arriving service users.

[[FIGURE:figure_2_risk_ratio.png|Ratio of worried-well to genuinely infected population over the 50-day horizon.|fig2]]

### 7.2 Demand uncertainty

Under default behaviour, the conditional mean demand rises sharply, peaks after the earliest worried-well pressure, and then declines gradually. The shaded band shows the generated fifth-to-ninety-fifth percentile range at each day, so its vertical width represents stochastic workload uncertainty rather than uncertainty in the compartment equations. Capacity with an asymmetric shortage penalty is selected from the upper portion of this daily distribution, not from the plotted mean alone. The band widens when the mean is high because the coefficient of variation is fixed. Its interpretation is limited by the assumed truncated-normal family, baseline \(CV=0.15\), and assumed values of \(p_P=1\) and \(p_W=0.5\).

[[FIGURE:figure_3_demand_uncertainty.png|Daily consultation-demand uncertainty under default behaviour.|fig3]]

Capacity combines the behavioural dynamics and demand uncertainty and therefore does not simply reproduce either compartment curve. With baseline uncertainty and costs, high contact produces the earliest and highest capacity crest, default behaviour lies between the alternatives, and cautious behaviour produces a later, broader requirement. Reading the lines from left to right emphasizes a practical distinction: a lower early peak can be accompanied by a longer period of elevated workload. Capacity planners would therefore need to consider both surge height and duration. The result concerns one pooled daily resource with independent decisions; it does not specify staff mix, opening hours, or inter-day rescheduling.

[[FIGURE:figure_4_optimal_capacity.png|Optimized daily consultation capacity by behavioural regime.|fig4]]

The uncertainty-sensitivity panel shows that optimized total expected cost rises as the coefficient of variation increases in every behavioural regime. This pattern reflects a larger absolute mismatch between one chosen capacity and realized scenario demand; it does not imply a change in underlying compartment states. The cautious behavioural curve is highest in the displayed cost comparison, consistent with its longer period of combined pressure, while high contact is lowest in total mismatch cost despite its higher capacity crest. Consequently, peak capacity and horizon-total mismatch cost rank scenarios differently. Because the same relative cost assumptions are used throughout the left panel, the figure supports comparison across scenario settings, not monetary valuation.

### 7.3 Cost and service-level sensitivity

The right-hand panel of Figure 5 answers the cost component of the research question. When underage and overage costs are balanced, the optimized quantile and mean benchmark are close for the modelled distribution. Increasing the underage penalty shifts the critical fractile upward, creating more safety capacity and reducing exposure to shortage. The relative advantage of the optimized policy consequently grows: at \(c_u=10\), the signed relative reduction is [[VALUE:cost_cu_10_co_1|relative_cost_reduction_pct|.2f]] percent. Read the right panel as a comparison of policy rules under fixed \(c_o=1\), not as evidence that the chosen ratios are economically correct. Both axes depend on assumed linear costs, and the plotted percentage is a finite-sample out-of-sample comparison.

[[FIGURE:figure_5_sensitivity.png|Uncertainty and cost sensitivity; the right-hand panel fixes overage cost at c_o = 1.|fig5]]

### 7.4 Service-seeking and initial-condition sensitivity

Service-seeking sensitivity changes demand without changing the compartment paths. As \(p_W\) moves from its lower setting to full worried-well service seeking, each worried-well fraction contributes progressively more requests, raising conditional mean demand and the optimized workload requirement on days when \(I_W\) is material. The operational implication is direct: even if infection dynamics were held fixed, communication, access rules, remote triage, or public concern could alter consultation pressure through the service-conversion channel. The experiment does not estimate how any such intervention changes \(p_W\); it demonstrates why the parameter requires local evidence.

Initial conditions alter both the subsequent trajectory and its capacity consequence. Starting with relatively fewer worried-well people dampens early behavioural pressure, whereas starting with relatively fewer infected people and the baseline worried fraction delays the infected peak and changes the combined-demand path. This sensitivity warns against treating the baseline initial state as innocuous. Early state composition can affect the sequence of daily targets even when all rates, costs, and uncertainty settings are unchanged. These alternatives are coursework scenarios, not reconstructions of a particular outbreak.

### 7.5 Optimized policy versus mean-demand planning

For default behaviour and baseline costs, the optimized policy has aggregate out-of-sample cost [[VALUE:behaviour_alpha_1|optimized_total_cost|,.1f]] cost units, compared with [[VALUE:behaviour_alpha_1|mean_policy_total_cost|,.1f]] for rounded mean-demand planning. The signed relative reduction is [[VALUE:behaviour_alpha_1|relative_cost_reduction_pct|.2f]] percent. This comparison answers the central policy question: when shortage is more consequential than unused capacity, consultation targets should sit above mean demand by an uncertainty buffer determined by the cost ratio.

[[POLICY_TABLE]]

The balanced-cost edge case must be interpreted differently. Its signed relative difference is [[VALUE:cost_cu_1_co_1|relative_cost_reduction_pct|.4f]] percent, which is negative. The optimized finite-sample median policy performed very slightly worse than the rounded mean policy on the independent evaluation draw. The sign is preserved rather than clamped to zero, and the result is not described as an improvement. It is consistent with near-equivalent decision rules plus sampling variation, not evidence of a substantive disadvantage. At the higher shortage penalty, by contrast, the separation between the critical-fractile policy and the mean is operationally meaningful. Overall, behaviour determines *when and how much* capacity is required, uncertainty determines the size and cost of mismatch, and the cost ratio determines how far capacity should be moved toward shortage protection.

## 8. Discussion

The experiments answer the research question in three linked parts. First, daily consultation capacity should track the combined infected and worried-well demand process rather than the infected curve alone. Behavioural contact changes not only the peak infected fraction but also the timing and persistence of worried-well pressure. A cautious scenario can therefore require a lower but broader capacity response, while a high-contact scenario requires an earlier and sharper response. The ratio figure reinforces that non-infected concern can dominate the modelled state composition early, even though its contribution to demand is discounted by the baseline service probability.

Second, capacity should include an uncertainty buffer when shortage carries more weight than unused slots. The buffer is not a fixed number of places: it scales with the day-specific distribution, whose spread is proportional to conditional mean under the implemented coefficient-of-variation model. Increasing uncertainty raises mismatch cost even after capacity is optimized. Third, the shortage-to-overage ratio governs the appropriate service level. Mean-demand planning is particularly unsuitable under asymmetric costs, whereas balanced costs make the median-based and mean-based rules close enough that finite-sample noise can determine their ordering. Preserving the small negative balanced-cost result is important because suppressing it would overstate consistency.

The model also separates two levers that are often conflated. Alpha changes the interaction dynamics and therefore the compartments themselves; \(p_W\) changes the fraction of the worried-well compartment converted into service demand. Operational actions aimed at contact behaviour and those aimed at access, information, or triage need not have the same effect. This project does not estimate either intervention. It shows that an organization should measure both the evolving concerned population and its propensity to seek service if the objective is capacity planning.

Several project-domain limitations constrain application. All outputs are synthetic planning scenarios, and there is no empirical calibration to individual clinical records, appointments, surveillance, or local capacity. Service-seeking probabilities are assumed coursework inputs. The coefficient of variation and underage and overage costs are also assumptions, not calibrated economic quantities. The resource is a single pool, with no distinction among clinicians, rooms, call handlers, tests, urgency classes, or infected and worried-well streams. Each day is a repeated independent single-period decision: unused capacity does not carry forward, unmet demand is not queued, and capacity cannot be reallocated across time. The deterministic behavioural system also omits statistical uncertainty in parameters and structure.

These limitations suggest a clear sequence for practical extension. Local request and state-classification information would be needed to estimate service conversion and demand dispersion. Stakeholder elicitation could ground shortage and overage consequences. A multi-resource queueing or stochastic programme could represent workforce, rooms, test types, priority classes, carry-over, and adjustment costs. Parameter uncertainty could be propagated jointly with demand noise. Such additions should follow validation of the simple mechanism, because added operational detail cannot compensate for an unsupported demand link.

Two implementation edge cases sit outside the project domain and should be distinguished from those substantive limitations. Demand and capacity are validated as non-negative integers only within the signed 64-bit arithmetic range; larger inputs are rejected rather than analysed. Separately, extremely disproportionate positive finite cost ratios can approach floating-point precision limits and require numerical checking before interpretation. Neither issue affects the recorded coursework scenarios, but both define the safe computational boundary. Finally, all policy comparisons are finite-sample out-of-sample evidence. Seeds make the reported experiment reproducible, not universal; alternative draws would produce small numerical changes, especially where competing rules are nearly equivalent.

## 9. Conclusion

Daily consultation capacity in this synthetic early-outbreak model should be driven by joint infected and worried-well demand, adjusted upward from mean demand when shortages are more costly than unused slots. Behaviour determines the timing and shape of the capacity curve: cautious interaction delays and broadens pressure, whereas high contact produces an earlier, higher crest. Demand uncertainty enlarges mismatch cost and the need for safety capacity. Increasing the underage penalty strengthens the case for a critical-fractile policy, while balanced costs yield near-equivalent rules and a slightly negative finite-sample comparison that must be retained.

The principal operational lesson is therefore conditional rather than prescriptive. Representing worried-well behaviour can materially change when capacity is needed, but the size of the response depends on assumed service seeking, uncertainty, and costs. The experiment provides a reproducible bridge from behavioural compartments to a daily newsvendor decision. It does not establish a clinical schedule for any provider. Empirical calibration, resource disaggregation, and multi-period constraints would be required before the framework could support a real deployment decision.

## References

- [[REFERENCE:allen_2017]]
- [[REFERENCE:asmundson_taylor_2020]]
- [[REFERENCE:blyuss_kyrychko_2005]]
- [[REFERENCE:chatterjee_2020]]
- [[REFERENCE:hick_2004]]
- [[REFERENCE:qin_2011]]
- [[REFERENCE:singh_gromov_2025]]
- [[REFERENCE:singh_rebennack_2026]]

## Appendix A. Reproducibility

Regenerate the complete evidence set from the repository root with:

`python scripts/run_analysis.py`

- in-sample seed = 6186
- out-of-sample seed = 6187
- in-sample scenarios = 5,000
- out-of-sample scenarios = 10,000

The generated contract consists of four CSV files in `outputs/data` and five PNG files in `outputs/figures`. Validate source integrity before building the document with:

`python scripts/validate_report_sources.py`
