# SCOPE – Cross-Platform Personal Data Explorer

SCOPE is a research prototype for large-scale discovery and analysis of personal information across social platforms.  
It is designed to be usable by non-expert users (e.g., regular social network users, security officers, privacy analysts) who want to understand which data about them or their organisation can be easily retrieved online.

Starting from a small set of identity clues (such as a name, surname, a reference image, or known profile URLs), SCOPE discovers candidate accounts, consolidates their publicly available content, and presents the results in an integrated cross-platform view. The system also includes a Retrieval-Augmented Generation (RAG) profiling module that can generate natural-language summaries and explanations grounded in the collected data.

> ⚠️ **Research prototype only.**  
> This project is intended for research and educational purposes. When using SCOPE, you must comply with the terms of service of each platform and with applicable privacy and data protection laws.

---

## Main Features

- **Automatic Search**  
  Discover candidate social profiles starting from minimal identity information (name, surname, reference photo).

- **Manual Search**  
  Investigate a set of known accounts by providing profile URLs or company-related information.

- **Identity-Aware Consolidation**  
  Use facial recognition models to filter and align accounts that most likely belong to the same individual.

- **Cross-Platform View**  
  Aggregate and normalise publicly available content from multiple platforms into a single representation.

- **RAG-Based Profiling**  
  Query the collected data via a conversational interface that uses a Retrieval-Augmented Generation (RAG) pipeline to produce human-readable explanations.

---

## Repository Overview

The most relevant elements of the repository are:

- `accounts.json`  
  Main configuration file where you specify the social accounts to be processed.

- `setup/`  
  Contains environment / dependency setup scripts, in particular:
  - `setup/setup.bat` – Windows setup script to install dependencies and prepare the environment.

- `Input-Examples/`  
  Example inputs for testing the system.

  - `Input-Examples/image/`  
    Example images that can be used as reference photos for Automatic Search.

- Other source-code directories  
  Contain the implementation of the scrapers, facial recognition module, RAG pipeline, and user interface.

---

## Requirements

- **Operating System**  
  Windows is recommended (a `setup.bat` script is provided). Other OSes may require manual configuration.

- **Software**
  - Python 3.x
  - A modern web browser (if the UI runs in the browser)
  - Python libraries for:
    - Web scraping (e.g., Selenium, BeautifulSoup)
    - Company-related data collection (e.g., Hunter API, StaffSpy)
    - Facial recognition (e.g., DeepFace, face_recognition with models such as Facenet, VGG-Face, ArcFace)
    - RAG / LLM interaction (e.g., golden-verba / Verda RAG)

Check the project’s dependency files (e.g., `requirements.txt` or equivalent) for the precise list of packages and versions.

---

## Getting Started

This section explains the minimal steps required to start using SCOPE.

### 1. Configure Social Accounts (`accounts.json`)

To begin using SCOPE, you must first specify which social accounts you want to analyse.

1. Open:

   ```text
   accounts.json
   ```

2. Add the accounts and/or company information you want to inspect.  
   Typical entries may include:
   - Platform identifier (e.g., `linkedin`, `instagram`, `twitter`, …)
   - Profile URL(s) or usernames
   - Optional metadata (e.g., notes, tags, organisation)

3. Save the file.

> ✅ **Important:** This file is the main input for SCOPE. If it is empty or misconfigured, the system will not have accounts to process.

### 2. Run the Setup Script (`setup/setup.bat`)

Before running the application for the first time, execute the setup script to prepare the environment:

```bash
cd setup
setup.bat
```

The script typically:
- Installs required Python packages
- Downloads or initialises models and resources
- Prepares configuration files and directories

If you are using a non-Windows system, you may need to replicate manually the steps performed by `setup.bat` (for example, by creating a virtual environment and installing dependencies).

---

## Example Images

SCOPE supports Automatic Search by using a reference photo of the target user.

- Example images are provided in:

  ```text
  Input-Examples/image/
  ```

You can use these images to quickly test the system.  
If you want to add your own images:

1. Place the image file inside `Input-Examples/image/`.
2. Label the file with the **name and surname** of the user you want to search for (e.g., `Jane_Doe.jpg`, `Mario_Rossi.png`), following the naming convention used in the rest of the system.
3. Ensure the image is of sufficient quality for facial recognition (face clearly visible).

---

## Workflows

SCOPE supports two main workflows.

### Manual Search

Manual Search is used when you already know some accounts or company information:

1. Add the relevant profile URLs and/or company identifiers to `accounts.json`.
2. Run `setup/setup.bat` (if not already done).
3. Launch the SCOPE application using the appropriate entrypoint script (see the source code for the main module).
4. Inspect the results:
   - View aggregated information per user
   - Explore posts and attributes collected from each platform
   - Identify redundant or sensitive information that is publicly exposed

### Automatic Search

Automatic Search is used when you start from minimal identity clues (name, surname, reference photo):

1. Place the reference photo in `Input-Examples/image/`, labelled with the user’s name and surname.
2. Provide the corresponding identity information in the application interface or configuration.
3. Run SCOPE; the system will:
   - Query supported platforms for candidate accounts
   - Apply facial recognition to filter and score candidates
   - Build a Verified Profile Set with the best matches per platform
4. Analyse the consolidated results and, if needed, refine thresholds or inputs.

---

## Outputs

Depending on the configuration and UI, SCOPE can produce:

- Consolidated profile views per user across platforms
- Lists of discovered accounts (candidate and verified)
- Extracted attributes and posts from each platform
- RAG-based summaries and explanations of the user’s online exposure

These outputs are intended to help users:

- Understand how much of their personal information is publicly available
- Identify potentially sensitive data
- Motivate privacy and security improvements (e.g., adjusting settings, removing content)

---

## Ethical and Legal Considerations

- Only use SCOPE on data and accounts that you are legally allowed to analyse.
- Respect the terms of service of target platforms.
- Be transparent with individuals if their profiles are being analysed in a research or organisational context.
- Do **not** use this tool for harassment, stalking, doxxing, or any other malicious activity.

---

## Citation

If you use SCOPE in a scientific publication, please cite the accompanying demo paper (add the final reference here once available).

```bibtex
@inproceedings{cirillo2026,
  title={Automated and Manual Web-Scale Discovery]{Automated and Manual Web-Scale Discovery of Personal Information with RAG-Driven Profiling},
  author={Cirillo, S., Polese, G., Solimando, G., and Zannone, N.},
  booktitle={TBD},
  year={2026}
}
```

---

## Contact

This project is part of ongoing research on privacy, security, and cross-platform analysis of personal information.  
For questions, feedback, or collaboration opportunities, please refer to the contact information provided in the associated scientific paper.
