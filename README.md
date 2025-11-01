<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/PulseLine-Agent/PulseLine">
    <img src=".github\Images\PulseLine.png" alt="Logo" width="320" height="320">
  </a>

<h3 align="center">PulseLine</h3>

  <p align="center">
    Your personal 24/7 online medical assistant.
    <br />
    <a href="https://github.com/PulseLine-Agent/PulseLine"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/PulseLine-Agent/PulseLine">View Demo</a>
    &middot;
    <a href="https://github.com/PulseLine-Agent/PulseLine/issues/new?labels=bug&template=bug-report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/PulseLine-Agent/PulseLine/issues/new?labels=enhancement&template=feature-request.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to develop an Agentic AI voice assistant for medical offices that automates routine patient requests both on the phone and online. Using real-time voice transcription and intelligent decision-making, the system can autonomously handle common tasks like scheduling appointments, refilling prescriptions, finding available doctors, or redirecting calls—helping reduce the administrative burden on healthcare professionals. Designed during the last week of the STEM Immersion phase of the Massachusetts Institute of Technology (MIT) Introduction to Technology, Engineering, and Science (MITES) for the Quest for Autonomy class.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

[![FastAPI][FastAPI.svg]][FastAPI-url]
[![Uvicorn][Uvicorn.svg]][Uvicorn-url]
[![Jinja2][Jinja2.svg]][Jinja2-url]
[![Twilio][Twilio.svg]][Twilio-url]
[![GroqCloud][GroqCloud.svg]][GroqCloud-url]
[![Websocket][Websocket.svg]][Websocket-url]
[![PostgreSQL][PostgreSQL.svg]][PostgreSQL-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

We recommend you create a Conda Environment but it's not required.
  ```sh
  conda create --name PulseLine python=3.12
  conda activate PulseLine
  ```

You will need [ngrok](https://ngrok.com) for this project if you'd like others to access it. Download and create a account before following the instructions to create a auth token before continuing.

You will also need [PostgreSQL](https://www.postgresql.org) for this project. Download it, create a database, make a table with the following headers:
  1. Patient ID
  2. First Name
  3. Last Name
  4. Date of Birth
  5. Gender
  6. Phone Number
  7. Email
  8. Address
  9. Insurance Provider
  10. Last Visit Date
  11. Primary Diagnosis
  12. Allergies
  13. Prescription
  14. Emergency Contact Name
  15. Emergency Contact Number
  16. Next Visit Date
  17. Doctor

Make sure to fill in all the columns. We recommend using a spreadsheet software that exports into a common file type for this.

You will also need [Twilio](https://www.twilio.com/en-us) for this project if you'd like others to call in. Follow the instructions to create an account before going to the console and under the left side bar, under manage, click active numbers and register a number.

This is an example of how to list things you need to use the software and how to install them. This project was created using python 3.12.0 64x bit.
  ```sh
  pip install -r requirements.txt
  ```

### Installation

1. Get a free API Key at [GroqCloud](https://console.groq.com/keys)
2. Clone the repo
   ```sh
   git clone https://github.com/PulseLine-Agent/PulseLine.git
   ```
3. Create a .env file in the main folder
4. Enter your API key in `.env`
   ```.env
   GROQ_API_KEY = ENTER_YOUR_API_KEY
   OPENAI_API_KEY = ENTER_YOUR_API_KEY

   USER = ENTER_POSTGRESQL_USER
   PASSWORD = ENTER_POSTGRESQL_PASSWORD
   DATABASE = ENTER_POSTGRESQL_DATABASE_NAME
   HOST = ENTER_POSTGRESQL_HOST
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin PulseLine-Agent/PulseLine
   git remote -v
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

To run the project, follow the following steps.

1. Run server.py.
  ```sh
  python server.py
  ```

2. Open a separate terminal and make your localhost public.
  ```sh
  ngrok http 8000
  ```

3. With the address ngrok gives you, go to Twilio's console's [active numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming) and under your number, you should see a text box on the same row as "A call comes in" named URL. There, put your forwarding address (i.e., https://0bb469d47dfd.ngrok-free.app).

Congratulations, you now have a running project! To access the model, either call into the active number or use the forwarding address!

To see evaluations, please head to 'eval.py' to see how your agent fares.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [x] On-call Personal Assistant
- [x] Online Personal Assistant
- [x] Frontend Online
- [x] Call-in Online
- [x] Mock Database
- [x] Medical Professional Transfer
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/PulseLine-Agent/PulseLine/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

We'll do our best to return feedback and incorporate your changes into our project!

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/PulseLine-Agent/PulseLine/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=PulseLine-Agent/PulseLine" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.md` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Jesse Wang - [LinkedIn](https://www.linkedin.com/in/jesse-h-wang) - jessewang2158@gmail.com - +1(860)-266-9870

Mohammad Islam - [LinkedIn](https://www.linkedin.com/in/mohammad-islam-04b015326/) - mohammadzislam08@gmail.com - +1(818)-232-6936

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Our thanks to [speech_recognition](https://github.com/Uberi/speech_recognition), [pydub](https://github.com/jiaaro/pydub), and [python-dotenv](https://github.com/theskumar/python-dotenv). This project would not have been possible without these authors' great libraries.

Also, a special thanks to Twilio's great [guide](https://github.com/twilio-samples/speech-assistant-openai-realtime-api-python) on building a voice assistant, [Best-README-Template](https://github.com/othneildrew/Best-README-Template/tree/main), [GroqStreamChain](https://github.com/The-Data-Dilemma/GroqStreamChain/tree/main), as well as [ChatGPT](https://chatgpt.com) for helping us out when creating this project.

Additionally, thanks to Freepik for providing the background image of the website.

If you'd like to read our report on the application, the link can be found [here](https://docs.google.com/document/d/198WE5Y-mSl6m6rdvJKZvhquq1ucRBFqGu5H7SpqzwM4/edit?usp=sharing)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/PulseLine-Agent/PulseLine.svg?style=for-the-badge
[contributors-url]: https://github.com/PulseLine-Agent/PulseLine/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/PulseLine-Agent/PulseLine.svg?style=for-the-badge
[forks-url]: https://github.com/PulseLine-Agent/PulseLine/network/members

[stars-shield]: https://img.shields.io/github/stars/PulseLine-Agent/PulseLine.svg?style=for-the-badge
[stars-url]: https://github.com/PulseLine-Agent/PulseLine/stargazers

[issues-shield]: https://img.shields.io/github/issues/PulseLine-Agent/PulseLine.svg?style=for-the-badge
[issues-url]: https://github.com/PulseLine-Agent/PulseLine/issues

[license-shield]: https://img.shields.io/github/license/PulseLine-Agent/PulseLine.svg?style=for-the-badge
[license-url]: https://github.com/PulseLine-Agent/PulseLine/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/mitesatmit

[FastAPI.svg]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com

[Jinja2.svg]: https://img.shields.io/badge/jinja-white.svg?style=for-the-badge&logo=jinja&logoColor=black
[Jinja2-url]: https://jinja.palletsprojects.com/en/stable

[Twilio.svg]: https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=Twilio&logoColor=white
[Twilio-url]: https://www.twilio.com/en-us

[Uvicorn.svg]: https://img.shields.io/badge/Uvicorn-7A00B2?style=for-the-badge&logo=gunicorn&logoColor=FFB7C3&labelColor=0A0068
[Uvicorn-url]: https://www.uvicorn.org

[GroqCloud.svg]: https://img.shields.io/badge/GroqCloud-white?style=for-the-badge&logo=groupon&logoColor=white&labelColor=orange
[GroqCloud-url]: https://console.groq.com/home

[Websocket.svg]: https://img.shields.io/badge/Websockets-gold?style=for-the-badge&logo=elegoo&logoColor=Blue&labelColor=blue
[Websocket-url]: https://websockets.readthedocs.io/en/stable

[PostgreSQL.svg]: https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white
[PostgreSQL-url]: https://www.postgresql.org
