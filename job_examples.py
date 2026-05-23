# One highly relevant job description per Master's program (30 total)
# Keys: Emoji + Job Title | Values: realistic job posting text
# Order mirrors MASTER_SECTIONS in app.py

JOB_EXAMPLES = {

    # ── Architecture ────────────────────────────────────────────────────────────
    "🏛️ Architect / Urban Planner": """Position: Senior Architect – Sustainable Design
Location: Lausanne, Switzerland
Award-winning architecture studio seeks an architect passionate about sustainability and innovation.
Responsibilities:
- Design positive-energy buildings (BIPV, passive house standards).
- Master parametric design using Rhino, Grasshopper, and Revit.
- Urban planning and public space management.
- Heritage conservation and architectural rehabilitation.
- Coordinate with structural, MEP engineers, and stakeholders.
- Advanced graphic representation (rendering, BIM, physical models).
Skills Required:
- Knowledge of Swiss SIA standards and LEED / Minergie certifications.
- Architectural theory and art history.
- Interdisciplinary collaboration in a multilingual environment.""",

    # ── Molecular and Biological Chemistry ──────────────────────────────────────
    "🔬 Medicinal Chemistry Researcher": """Position: Research Scientist – Medicinal Chemistry
Location: Basel, Switzerland
Leading pharmaceutical company seeks a medicinal chemist to drive early-stage drug discovery.
Responsibilities:
- Design, synthesise, and characterise novel small-molecule drug candidates.
- Structure-Activity Relationship (SAR) optimisation using computational tools.
- NMR, mass spectrometry, and HPLC analysis of synthesised compounds.
- Collaboration with structural biology and pharmacology teams.
- Interpret binding affinity and ADMET data to guide lead optimisation.
Skills Required:
- Organic synthesis (multi-step, asymmetric catalysis).
- Computational chemistry: molecular docking, pharmacophore modelling.
- Strong understanding of biochemistry and cell biology assays.
- Experience with drug target classes: kinases, GPCRs, proteases.""",

    # ── Data Science ─────────────────────────────────────────────────────────────
    "📊 Data Scientist / ML Engineer": """Position: Senior Data Scientist – AI Products
Location: Zurich, Switzerland
We are building the next generation of AI-powered analytics tools.
Responsibilities:
- Develop and deploy machine learning models (classification, regression, ranking, GenAI).
- Design end-to-end ML pipelines: data ingestion, feature engineering, training, serving.
- Implement NLP and LLM fine-tuning workflows (RAG, RLHF, prompt engineering).
- Analyse large-scale datasets using Spark, BigQuery, and Pandas.
- Collaborate with product and engineering to translate models into production.
Skills Required:
- Deep expertise in PyTorch / TensorFlow / Scikit-Learn.
- Strong foundation in statistics, probability, and linear algebra.
- MLOps: MLflow, Weights & Biases, Kubernetes-based serving.
- SQL and data warehousing best practices.
- Excellent Python coding and software engineering skills.""",

    # ── Chemical Engineering and Biotechnology ──────────────────────────────────
    "⚗️ Chemical Process Engineer": """Position: Process Engineer – Bioprocess Development
Location: Visp, Switzerland
Lonza is hiring a process engineer to scale biopharmaceutical manufacturing.
Responsibilities:
- Design and optimise upstream/downstream bioprocesses (fermentation, chromatography).
- Mass and energy balance calculations for scale-up from lab to pilot to production.
- Implement Process Analytical Technology (PAT) for real-time monitoring.
- Regulatory compliance: cGMP, ICH guidelines, process validation.
- Techno-economic analysis and HAZOP studies.
Skills Required:
- Unit operations: distillation, filtration, extraction, crystallisation.
- Bioreactor design and cell culture (mammalian, microbial).
- Modelling with Aspen Plus or MATLAB.
- Understanding of thermodynamics, reaction kinetics, and transport phenomena.
- Familiarity with Quality by Design (QbD) principles.""",

    # ── Civil Engineering ─────────────────────────────────────────────────────────
    "🏗️ Structural Civil Engineer": """Position: Structural Civil Engineer
Location: Fribourg, Switzerland
Design sustainable infrastructure, bridges, and buildings for the next century.
Responsibilities:
- Structural analysis and design of reinforced concrete, steel, and timber structures.
- Geotechnical engineering: foundation design, slope stability, soil mechanics.
- BIM-based project delivery using Revit and Civil 3D.
- Hydraulics, hydrology, and stormwater management for urban networks.
- Environmental impact assessments and sustainability reporting.
Skills Required:
- FEM software: SAP2000, Robot Structural Analysis, ABAQUS.
- Swiss standards (SIA 260/261/262) and Eurocodes.
- Seismic design and wind load analysis.
- Project management and site supervision experience.
- AutoCAD and GIS tools for spatial analysis.""",

    # ── Mechanical Engineering ─────────────────────────────────────────────────────
    "⚙️ Mechanical Design Engineer": """Position: Mechanical Design Engineer – Precision Systems
Location: Bern, Switzerland
Join our team developing high-precision mechanical systems for industrial robotics.
Responsibilities:
- 3D CAD design and assembly modelling (SolidWorks, CATIA, Siemens NX).
- Finite Element Analysis (FEA) for structural integrity and fatigue (ANSYS, Abaqus).
- Thermodynamics and heat transfer analysis for thermal management.
- Fluid mechanics and aerodynamics simulations (CFD with OpenFOAM / Fluent).
- Rapid prototyping: 3D printing, CNC machining, tolerance stack-up analysis.
Skills Required:
- GD&T (Geometric Dimensioning and Tolerancing) and metrology.
- Mechanisms, kinematics, and dynamics.
- Materials selection: metals, polymers, composites.
- Knowledge of manufacturing processes: casting, forging, machining.
- DFMA (Design for Manufacture and Assembly) principles.""",

    # ── Nuclear Engineering ──────────────────────────────────────────────────────
    "☢️ Nuclear Engineer": """Position: Nuclear Systems Engineer
Location: Würenlingen (PSI), Switzerland
Paul Scherrer Institut seeks an engineer for advanced reactor and safety research.
Responsibilities:
- Neutronics modelling and reactor core design using Monte Carlo (MCNP/OpenMC).
- Thermal-hydraulics analysis of reactor cooling systems (RELAP5, TRACE).
- Radiation shielding calculations and dose assessment.
- Fuel cycle analysis and nuclear waste management strategies.
- Safety analysis and probabilistic risk assessment (PRA/PSA).
Skills Required:
- Nuclear physics: fission, neutron transport, decay heat.
- Knowledge of PWR, BWR, and advanced reactor concepts (Gen IV, SMRs).
- Materials science under irradiation conditions.
- Regulatory frameworks: IAEA safety standards, ENSI requirements.
- Programming: Python, FORTRAN, or C++ for nuclear codes.""",

    # ── Electrical and Electronic Engineering ────────────────────────────────────
    "⚡ Electrical / Hardware Engineer": """Position: Hardware / Electrical Engineer – Embedded Systems
Location: Neuchâtel, Switzerland
Develop high-performance electronic systems for IoT and medical devices.
Responsibilities:
- PCB design and layout (Altium Designer, KiCad): analog and mixed-signal circuits.
- FPGA programming (VHDL / Verilog) for real-time signal processing.
- Embedded firmware development (C/C++, STM32, ARM Cortex-M).
- Signal processing: filtering, ADC/DAC, RF design, antenna matching.
- Power electronics: DC-DC converters, motor drives, battery management systems.
Skills Required:
- Schematic capture, simulation (SPICE), and hardware debugging.
- EMC/EMI compliance testing (CE marking, FCC).
- Communication protocols: SPI, I2C, UART, CAN, BLE, Zigbee.
- Oscilloscope, logic analyser, and network analyser proficiency.
- Safety standards for medical electronics (IEC 60601).""",

    # ── Digital Humanities ──────────────────────────────────────────────────────────
    "📚 Digital Humanities Specialist": """Position: Digital Humanities Researcher / Data Curator
Location: Geneva, Switzerland
Cultural heritage institution seeks a digital humanities expert.
Responsibilities:
- Build and curate large digital corpora (text, images, audio, manuscripts).
- Apply NLP techniques: named entity recognition, topic modelling, OCR post-correction.
- Develop web-based digital editions and interactive visualisations (D3.js, Gephi).
- Design ontologies and linked data schemas (RDF, OWL, CIDOC-CRM).
- Collaborate with historians, archivists, and software engineers.
Skills Required:
- Programming: Python (spaCy, NLTK, Hugging Face), SPARQL, TEI/XML.
- Database systems: relational and graph databases (Neo4j).
- Knowledge of archival science, library standards (Dublin Core, IIIF).
- Critical analysis of algorithmic bias in cultural datasets.
- Science communication and academic writing.""",

    # ── Computer Science ────────────────────────────────────────────────────────────
    "💻 Software Engineer (Backend / Systems)": """Position: Senior Software Engineer – Distributed Systems
Location: Zurich, Switzerland
Fast-growing fintech building real-time payment infrastructure at scale.
Responsibilities:
- Design and implement high-throughput, fault-tolerant distributed systems.
- Build RESTful and gRPC APIs; microservices architecture on Kubernetes.
- Database design: PostgreSQL, Cassandra, Redis, and event streaming with Kafka.
- Write clean, testable code in Go or Java; contribute to open-source projects.
- Performance profiling, load testing, and production incident response.
Skills Required:
- Deep understanding of OS concepts, networking (TCP/IP, HTTP/2, TLS).
- Algorithms and data structures: complexity analysis, optimisation.
- Concurrency models: threads, async/await, actor model.
- CI/CD pipelines, GitOps, infrastructure-as-code (Terraform).
- Security best practices: OAuth2, RBAC, secret management.""",

    # ── Computer Science - Cybersecurity ─────────────────────────────────────────────
    "🔐 Cybersecurity Engineer": """Position: Cybersecurity Engineer – Offensive & Defensive Security
Location: Zurich, Switzerland
Elite security team protecting critical financial and cloud infrastructure.
Responsibilities:
- Conduct penetration testing (web, network, cloud, mobile) and red team exercises.
- Vulnerability research and responsible disclosure (CVE assignments).
- Implement and tune SIEM, IDS/IPS, and EDR solutions.
- Cryptographic protocol design and security proofs (formal verification).
- Threat modelling (STRIDE, PASTA) and secure SDLC integration.
Skills Required:
- Network security: firewalls, VPNs, packet capture analysis (Wireshark).
- Malware analysis, reverse engineering (Ghidra, IDA Pro).
- Cloud security: AWS/Azure security architecture, IAM policies.
- Applied cryptography: TLS, PKI, zero-knowledge proofs, post-quantum schemes.
- CTF experience and knowledge of MITRE ATT&CK framework.""",

    # ── Life Sciences Engineering ───────────────────────────────────────────────
    "🧬 Biomedical Engineer": """Position: R&D Biomedical Engineer – Medical Devices
Location: Geneva, Switzerland
Design the next generation of wearable and implantable medical devices.
Responsibilities:
- Biosignal acquisition and processing (EEG, ECG, EMG) using Python and MATLAB.
- Mechanical design of implants and prosthetics (biomaterials, FEA).
- Microfluidics and lab-on-chip device fabrication (PDMS, photolithography).
- Medical imaging analysis: segmentation and registration (MRI, CT, ultrasound).
- Regulatory pathway: ISO 13485, FDA 510(k), MDR (EU) technical documentation.
Skills Required:
- Physiology and biomechanics fundamentals.
- Embedded systems for medical sensors (low-power BLE, wireless telemetry).
- Biocompatibility testing and sterilisation protocols.
- Signal processing: digital filters, FFT, wavelet transforms.
- Clinical study design and statistical analysis (MATLAB, R).""",

    # ── Financial Engineering ────────────────────────────────────────────────────
    "📈 Quantitative Finance Engineer": """Position: Quantitative Analyst (Quant) – Derivatives Pricing
Location: Geneva, Switzerland
Global asset manager seeks a quantitative engineer for structured products.
Responsibilities:
- Develop and calibrate pricing models (Black-Scholes, Heston, SABR, LMM).
- Implement risk management tools: Greeks, VaR, Expected Shortfall, CVA.
- Build high-performance backtesting frameworks in Python and C++.
- Statistical arbitrage and algorithmic trading strategy research.
- Machine learning for financial forecasting: LSTM, gradient boosting, factor models.
Skills Required:
- Stochastic calculus, Itô's lemma, PDE methods (finite differences).
- Time series analysis: ARIMA, GARCH, Kalman filter.
- Monte Carlo simulation and variance reduction techniques.
- Market microstructure and execution algorithms (TWAP, VWAP).
- Bloomberg / Refinitiv data APIs and SQL for financial databases.""",

    # ── Applied Mathematics ──────────────────────────────────────────────────────
    "🧮 Applied Mathematics Engineer": """Position: Applied Mathematician – Optimisation & Simulation
Location: Lausanne, Switzerland
Engineering consultancy seeks an applied mathematician for industrial R&D.
Responsibilities:
- Formulate and solve large-scale optimisation problems (LP, MIP, SOCP, NLP).
- Develop numerical methods for PDEs: FEM, FVM, spectral methods.
- Mathematical modelling of physical, biological, and economic systems.
- Inverse problems and uncertainty quantification (Bayesian inference, UQ).
- Implement efficient algorithms in Python, Julia, or C++.
Skills Required:
- Analysis, functional analysis, and measure theory.
- Numerical linear algebra: sparse solvers, preconditioning, iterative methods.
- Control theory and dynamical systems (stability analysis, optimal control).
- Graph theory and network optimisation.
- Scientific computing tools: NumPy, SciPy, FEniCS, CVXPY.""",

    # ── Physics Engineering ──────────────────────────────────────────────────────
    "🔭 Physics / Instrumentation Engineer": """Position: Instrumentation Physicist – R&D Lab Systems
Location: Geneva (CERN area), Switzerland
High-energy physics facility seeks an instrumentation engineer.
Responsibilities:
- Design and characterise particle detectors (silicon strips, scintillators, calorimeters).
- Develop data acquisition (DAQ) systems and real-time FPGA readout electronics.
- Optical instrumentation: laser systems, interferometry, fibre optics.
- Vacuum technology, cryogenics, and ultra-high precision measurement.
- Data analysis pipelines for large-scale experimental datasets.
Skills Required:
- Electromagnetism and optics at graduate level.
- Analog and digital electronics for low-noise signal chains.
- LabVIEW, ROOT, or Python for instrument control and data analysis.
- Knowledge of accelerator physics or detector physics.
- Technical writing for scientific publications and internal reports.""",

    # ── Sustainable Management and Technology ───────────────────────────────────
    "🌱 Sustainability Manager / ESG Analyst": """Position: Sustainability Strategy Manager
Location: Zug, Switzerland
Global corporation integrating ESG into core business strategy.
Responsibilities:
- Design and execute corporate sustainability roadmaps aligned to Science-Based Targets.
- Life Cycle Assessment (LCA) of products and supply chains using SimaPro or OpenLCA.
- Report under GRI, TCFD, CSRD, and CDP frameworks.
- Manage carbon accounting (Scope 1/2/3) and design offset/insetting strategies.
- Stakeholder engagement: investors, regulators, NGOs, and internal leadership.
Skills Required:
- Deep knowledge of sustainability standards and ESG rating methodologies.
- Circular economy principles and sustainable business model innovation.
- Data analysis: Excel, Python, Power BI for ESG KPI dashboards.
- Understanding of climate science and policy (Paris Agreement, EU Taxonomy).
- Strong communication and cross-functional project management skills.""",

    # ── Management, Technology and Entrepreneurship ──────────────────────────────
    "🚀 Product Manager / Tech Entrepreneur": """Position: Technical Product Manager – B2B SaaS
Location: Zurich, Switzerland
High-growth startup building enterprise AI tools for the manufacturing sector.
Responsibilities:
- Define product vision, strategy, and roadmap in close collaboration with engineering.
- Conduct customer discovery interviews, analyse usage data, and prioritise features.
- Write detailed product specs, user stories, and acceptance criteria.
- Lead cross-functional sprints (Agile/Scrum) with engineering, design, and sales.
- Go-to-market strategy: pricing, positioning, competitive analysis.
Skills Required:
- Technical background to credibly engage with software and ML engineers.
- Business model design (Value Proposition Canvas, Lean Canvas).
- Data-driven decision making: A/B testing, funnel analysis, cohort metrics.
- Venture capital landscape, startup financing, and pitch deck creation.
- Excellent written and verbal communication in English (French a plus).""",

    # ── Mathematics - Master ─────────────────────────────────────────────────────
    "∞ Mathematician / Actuary": """Position: Actuarial Analyst – Life & Pension Risk
Location: Zurich, Switzerland
Leading reinsurance firm seeks a mathematically rigorous actuarial analyst.
Responsibilities:
- Develop and validate stochastic mortality and longevity models.
- Risk capital modelling under Swiss Solvency Test (SST) and Solvency II.
- Perform asset-liability management (ALM) studies for pension portfolios.
- Pricing of life insurance products and structured reinsurance contracts.
- Mathematical foundations for catastrophe and extreme-value modelling.
Skills Required:
- Advanced probability theory, measure-theoretic statistics, stochastic processes.
- Extreme value theory and copula models for dependency structures.
- Programming: R, Python, and VBA for actuarial models.
- Exam progress toward SCOR / SAV / IFoA actuarial qualification.
- Financial mathematics: interest rate models, bond pricing, duration.""",

    # ── Micro- and Nanotechnologies for Integrated Systems ─────────────────────
    "🔬 MEMS / Nanotechnologies Engineer": """Position: MEMS & Nanotechnology Engineer
Location: Neuchâtel, Switzerland
CSEM is hiring an engineer to develop next-generation microsystems.
Responsibilities:
- Design MEMS sensors and actuators (accelerometers, pressure sensors, microvalves).
- Cleanroom microfabrication: photolithography, etching (RIE/DRIE), CVD, sputtering.
- Characterisation: SEM, AFM, profilometry, and electrical wafer testing.
- Heterogeneous integration: wafer bonding, flip-chip, and 3D packaging.
- System co-design integrating MEMS with CMOS readout circuits.
Skills Required:
- Solid-state physics and semiconductor device fundamentals.
- Finite element modelling of mechanical and electrostatic MEMS behaviour.
- Process design kit (PDK) flows for foundry tape-out.
- Lab-on-chip and microfluidic platform development.
- Thin-film deposition and nanopatterning techniques (e-beam lithography, NIL).""",

    # ── Microengineering ─────────────────────────────────────────────────────────
    "🔧 Microengineering Engineer": """Position: Precision Microtechnology Engineer – Watch & MedTech
Location: Le Locle, Switzerland
Leading Swiss watchmaker and medtech spinoff seeks a microtechnology engineer.
Responsibilities:
- Design ultra-precision mechanical components: escapements, micro-gears, springs.
- Electrical/optical micro-assembly and alignment to sub-micron tolerances.
- Miniaturised sensor integration for smartwatches and wearable medical devices.
- Coordinate with suppliers for micro-machining (EDM, laser cutting, electroforming).
- Reliability testing: shock, vibration, temperature cycling, long-term wear.
Skills Required:
- Precision mechanics, tribology, and surface engineering.
- Micro-optics and photonics (fibre alignment, VCSEL, photodetectors).
- Cleanroom assembly and wire bonding / flip-chip techniques.
- CAD for small-scale design (CATIA, SolidWorks micro-components).
- Metrology: coordinate measuring machines (CMM), interferometry.""",

    # ── Neuro-X ──────────────────────────────────────────────────────────────────
    "🧠 Computational Neuroscientist": """Position: Computational Neuroscientist / NeuroAI Researcher
Location: Lausanne, Switzerland
Blue Brain Project seeks a scientist at the intersection of AI and neuroscience.
Responsibilities:
- Build biologically realistic neural circuit models (spiking networks, Hodgkin-Huxley).
- Develop brain-computer interface (BCI) algorithms for neural decoding.
- Apply deep learning to neural time-series data (calcium imaging, LFP, EEG).
- Analyse large-scale connectomics and electrophysiology datasets.
- Translate neuroscience findings into neuromorphic computing architectures.
Skills Required:
- Computational modelling: NEURON, Brian2, or custom simulators.
- Machine learning: recurrent networks, attention mechanisms, variational autoencoders.
- Statistics for neuroscience: GLMs, dimensionality reduction (PCA, t-SNE, UMAP).
- Python, Julia, or MATLAB for scientific computing.
- Neuroimaging analysis: fMRI preprocessing (FSL, SPM), spike sorting.""",

    # ── Physics - Master ──────────────────────────────────────────────────────────
    "⚛️ Research Physicist": """Position: Research Physicist – Condensed Matter / Quantum Materials
Location: Lausanne (EPFL) / PSI Villigen
Cutting-edge physics laboratory seeks a postdoctoral or senior PhD-level physicist.
Responsibilities:
- Experimental investigation of topological insulators, superconductors, or 2D materials.
- Operate and maintain cryogenic measurement systems (dilution refrigerators, mK setups).
- Synchrotron and neutron scattering experiments (ARPES, neutron diffraction).
- Develop theoretical models for quantum phase transitions and emergent phenomena.
- Publish findings in high-impact journals; present at international conferences.
Skills Required:
- Quantum mechanics, statistical mechanics, and many-body theory.
- Materials characterisation: XRD, TEM, STM, optical spectroscopy.
- Low-temperature physics and cryogenic techniques.
- Numerical methods: DFT (VASP, Quantum ESPRESSO), Monte Carlo, tensor networks.
- Collaboration in large international research consortia.""",

    # ── Robotics ────────────────────────────────────────────────────────────────
    "🤖 Robotics Engineer": """Position: Robotics Software Engineer – Autonomous Systems
Location: Lausanne, Switzerland
Autonomous robot company building next-gen warehouse and logistics systems.
Responsibilities:
- Design and implement robot motion planning algorithms (SLAM, path planning, MPC).
- Develop perception pipelines using LiDAR, RGB-D, and event cameras.
- Real-time control systems for manipulators and mobile robots (ROS 2).
- Simulate robot behaviour in Gazebo, Isaac Sim, or MuJoCo.
- Deploy and maintain fleet management systems in production environments.
Skills Required:
- Rigid-body dynamics, kinematics, and control theory (PID, LQR, MPC).
- Computer vision: object detection (YOLO), pose estimation, optical flow.
- C++ and Python for high-performance real-time systems.
- Safety-critical software development (functional safety, IEC 61508).
- Knowledge of reinforcement learning for robot skill acquisition.""",

    # ── Materials Science and Engineering ────────────────────────────────────────
    "🧪 Materials R&D Engineer": """Position: Materials R&D Engineer – Energy Applications
Location: Sion, Switzerland
Battery startup developing next-generation solid-state electrolytes.
Responsibilities:
- Synthesise and characterise novel electrode and electrolyte materials.
- Characterisation techniques: SEM/TEM, XRD, XPS, EIS, BET surface area.
- Polymer science, ceramics, and composite material development.
- Thin-film deposition and surface functionalisation (ALD, PVD).
- Photovoltaics and semiconductor materials for solar cell optimisation.
Skills Required:
- Thermodynamics of materials, phase diagrams, and kinetics.
- Nanotechnology: nanoparticle synthesis, nanofabrication.
- Battery electrochemistry and cell testing (galvanostatic cycling, rate capability).
- Metallurgy and mechanical properties characterisation (tensile, hardness).
- Data analysis using Python or MATLAB for materials informatics.""",

    # ── Computational Science and Engineering ────────────────────────────────────
    "🖥️ Computational Science / HPC Engineer": """Position: HPC / Scientific Computing Engineer
Location: Lugano (CSCS), Switzerland
Swiss National Supercomputing Centre seeks a computational scientist.
Responsibilities:
- Optimise large-scale scientific simulation codes for GPU/CPU supercomputers.
- Develop parallel algorithms using MPI, OpenMP, CUDA, and HIP.
- Port legacy Fortran/C++ codes to modern architectures (A100, GH200 clusters).
- Build scalable workflows for physics, climate, and life-science simulations.
- Performance profiling: Nsight, VTune, Score-P, and Scalasca.
Skills Required:
- Numerical methods: PDE solvers, FFT, sparse linear algebra (PETSc, Trilinos).
- Software engineering: CMake, version control, CI/CD for scientific codes.
- Containerisation: Singularity, Spack, module systems on HPC clusters.
- Domain knowledge in at least one field: fluid dynamics, molecular dynamics, quantum chemistry.
- Strong C++17/20 and Python; optional: Julia, Chapel.""",

    # ── Quantum Science and Engineering ──────────────────────────────────────────
    "⚛️ Quantum Technology Engineer": """Position: Quantum Hardware Engineer – Superconducting Qubits
Location: Zurich, Switzerland
ETH/EPFL spinoff building scalable quantum processors for cloud quantum computing.
Responsibilities:
- Design, fabricate, and characterise superconducting qubit circuits (transmon, fluxonium).
- Implement quantum gate calibration and error mitigation protocols.
- Develop cryogenic microwave electronics and wiring for multi-qubit systems.
- Qubit coherence measurements: T1, T2, Ramsey, echo sequences.
- Collaborate on quantum error correction (surface code, CSS codes) implementation.
Skills Required:
- Quantum information theory: density matrices, quantum channels, entanglement.
- Quantum circuit simulation (Qiskit, Cirq, PennyLane).
- Microwave engineering: resonators, parametric amplifiers, directional couplers.
- Cryogenics: dilution refrigerator operation and troubleshooting.
- FPGA-based control electronics (Zurich Instruments, Qblox).""",

    # ── Energy Science and Technology ───────────────────────────────────────────
    "⚡ Energy Systems Engineer": """Position: Energy Systems Engineer – Grid Decarbonisation
Location: Geneva, Switzerland
Energy transition consultancy seeks an engineer to model future power systems.
Responsibilities:
- Model and optimise energy systems: electricity networks, hydrogen, heat storage.
- Power flow analysis and grid stability studies (load flow, short-circuit, dynamic).
- Design and integrate renewable energy projects (solar PV, wind, hydro, BESS).
- Techno-economic modelling of energy transition pathways (PyPSA, EnergyPLAN).
- Regulatory and market analysis: Swiss, EU energy law, capacity markets.
Skills Required:
- Power systems engineering: AC/DC transmission, HVDC, smart grid technologies.
- Thermodynamics of heat pumps, fuel cells, and thermal storage.
- Energy storage: battery chemistries, flow batteries, compressed air.
- Programming: Python (PyPSA, PandaPower), MATLAB/Simulink.
- Life cycle assessment (LCA) applied to energy systems.""",

    # ── Environmental Sciences and Engineering ───────────────────────────────────
    "🌍 Environmental Engineer": """Position: Environmental Engineer – Water & Climate
Location: Lausanne, Switzerland
Cantonal environmental agency and EPFL spinoff seek an environmental engineer.
Responsibilities:
- Hydrological modelling: rainfall-runoff, flood risk, groundwater flow (MODFLOW).
- Wastewater treatment design: biological processes, micropollutant removal.
- Air quality monitoring and atmospheric dispersion modelling (AERMOD, CALPUFF).
- Environmental risk assessment and remediation of contaminated sites.
- Climate change impact assessment and adaptation planning.
Skills Required:
- Environmental chemistry: geochemistry, fate and transport of pollutants.
- GIS and remote sensing (QGIS, ArcGIS, Google Earth Engine).
- Statistical analysis and uncertainty quantification (R, Python).
- Knowledge of Swiss and EU environmental regulations (GSchG, ChemRRV).
- Ecological engineering and nature-based solutions.""",

    # ── Statistics ───────────────────────────────────────────────────────────────
    "📉 Statistician / Biostatistician": """Position: Senior Biostatistician – Clinical Trials
Location: Basel, Switzerland
Top-10 pharma company seeks a senior biostatistician for oncology clinical development.
Responsibilities:
- Design adaptive clinical trials: sample size, randomisation, interim analyses.
- Statistical analysis plans (SAP) and pre-specified analysis for Phase II/III trials.
- Survival analysis (Kaplan-Meier, Cox PH), mixed models for repeated measures (MMRM).
- Regulatory submission packages: ICH E9/E9R1, FDA/EMA statistical guidance.
- Bayesian adaptive designs and master protocol development.
Skills Required:
- Mathematical statistics: likelihood theory, hypothesis testing, confidence intervals.
- Programming: R (survival, lme4, ggplot2), SAS (PROC MIXED, PROC LIFETEST).
- Causal inference: propensity scores, instrumental variables, estimands framework.
- Handling missing data: MCAR/MAR/MNAR mechanisms, multiple imputation.
- Communication of statistical results to non-statisticians and regulatory agencies.""",

    # ── Urban Systems ───────────────────────────────────────────────────────────
    "🏙️ Urban Systems Planner": """Position: Urban Systems Planner / Smart City Analyst
Location: Lausanne, Switzerland
Cantonal planning office and smart city startup seek an urban systems specialist.
Responsibilities:
- Develop data-driven urban mobility models (agent-based simulation, MATSim).
- Spatial analysis of land use, transport, and socio-economic inequality (GIS).
- Design digital twin frameworks for urban infrastructure (energy, water, transport).
- Participatory planning: community engagement, co-design workshops.
- Evaluate urban policies for climate resilience and social equity.
Skills Required:
- Urban planning theory, land use economics, and zoning law.
- Transport modelling: VISUM, TransCAD, or open-source equivalents.
- Programming: Python (GeoPandas, Shapely, OSMnx), R for spatial statistics.
- Remote sensing and LiDAR data for urban morphology analysis.
- Knowledge of Swiss spatial planning law (RPG, OAT) and smart city standards.""",
}