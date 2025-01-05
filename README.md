# OpportunAI

OpportunAI is an intelligent, AI-driven job application assistant designed to help you streamline your job search and boost your career prospects. With features tailored to modern job seekers, OpportunAI simplifies everything from crafting resumes and cover letters to tracking application statuses and preparing for interviews.

---

## Features

### AI-Powered Resume & Cover Letter Generator
- Create personalized resumes and cover letters tailored to specific job descriptions.
- Get professional suggestions for content improvement.

### Job Description Parsing
- Extract key qualifications and responsibilities from job postings effortlessly.

### Application Tracker
- Maintain a detailed log of all your applications, including company name, role, submission date, and status.
- Set reminders for deadlines and follow-ups.

### Interview Preparation Tools
- Generate potential interview questions and personalized tips based on job descriptions.

### Career Insights & Analytics
- Visualize application trends with detailed charts and insights.
- Highlight areas for improvement in your job search strategy.

---

## Installation

### Prerequisites
- Python 3.8+
- MySQL or PostgreSQL (for the application database)
- OpenAI API key

### Steps
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/opportunai.git
    cd opportunai
    ```

2. **Set Up a Virtual Environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database**:
    - Create a new MySQL or PostgreSQL database.
    - Update `config.py` with your database credentials.

5. **Configure the Application**:
    - Add your OpenAI API key to the `.env` file:
      ```env
      OPENAI_API_KEY=your_openai_api_key
      ```

6. **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

7. **Start the Application**:
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://localhost:8000`.

---

## Usage

1. **Sign Up or Log In**: Create a user profile to start managing your applications.
2. **Upload Your Resume**: OpportunAI will use it as a baseline for generating tailored resumes.
3. **Search Jobs**: Use the job description parser to extract insights from postings.
4. **Track Your Applications**: Add job applications to the tracker and stay updated on their status.
5. **Prepare for Interviews**: Use AI-powered tools for customized interview prep.

---

## Front-End Structure

The front-end of OpportunAI is structured as follows:


```
src/
├── components/
│   ├── Profile/
│   │   ├── ViewProfile.jsx
│   │   ├── EditProfile.jsx
│   ├── ResumeUpload/
│   │   ├── UploadResume.jsx
│   ├── Dashboard/
│   │   ├── Dashboard.jsx
├── pages/
│   ├── Login.jsx
│   ├── Signup.jsx
│   ├── ProfilePage.jsx
│   ├── DashboardPage.jsx
├── services/
│   ├── api.js
├── App.js
├── index.js
```

### Development Status

- **`components/` folder**: Completed.
- **Files**:
  - `DashboardPage.jsx`: Completed.
  - `ProfilePage.jsx`: Completed.

---

## Contributing

We welcome contributions from the community! To contribute:
1. Fork the repository and create a new branch:
    ```bash
    git checkout -b feature-name
    ```
2. Make your changes and commit them with descriptive messages.
3. Push to your fork and submit a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or feedback, please email **cnorris7@gmu.edu** or open an issue in the repository.
