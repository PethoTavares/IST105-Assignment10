# IST105 – Assignment 10  
### Django + REST APIs + MongoDB + AWS EC2

This project was developed for **IST105 Assignment 10** and implements a complete solution using **Django**, **MongoDB**, and two public APIs:  
- **REST Countries API**  
- **OpenWeatherMap API**

The application allows the user to select a continent, retrieve a list of random countries from that region, fetch the weather for each country’s capital city, and store all results inside a MongoDB database running on a separate EC2 instance.

---

## 1. System Architecture

The system uses two AWS EC2 instances:

### **1) WebServer-EC2 (Amazon Linux 2)**
- Runs the Django application  
- Installed: Python 3, Django, requests, pymongo  
- Exposes port **8000** for Django  
- Security Group Rules:
  - HTTP (80) → 0.0.0.0/0  
  - Custom TCP 8000 → 0.0.0.0/0  
  - SSH (22) → My IP  

### **2) MongoDB-EC2 (Ubuntu 22.04)**
- Hosts the MongoDB server  
- MongoDB installed using official `mongodb-org` package  
- Security Group Rules:
  - SSH (22) → My IP  
  - Custom TCP 27017 → WebServer-SG (or WebServer private IP)  

Both instances are inside the same VPC to allow internal communication.

---

## 2. APIs Used

### **REST Countries API**
- Endpoint: `https://restcountries.com/v3.1/region/{continent}`
- Used to get:
  - Country name  
  - Capital city  
  - Optional: population, lat/lng  

### **OpenWeatherMap API**
- Endpoint:  
  `https://api.openweathermap.org/data/2.5/weather?q={capital}&appid={API_KEY}&units=metric`
- Requires an API key  
- Used to return:
  - Temperature  
  - Weather description  
  - Other weather data  

The Django app first calls REST Countries, selects 5 random countries, then fetches the weather from OpenWeatherMap.

---

## 3. Django Application Structure
assignment10/
│── assignment10/
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── geoapp/
│ ├── views.py
│ ├── forms.py
│ ├── urls.py
│ └── templates/
│ ├── continent_form.html
│ ├── search_results.html
│ └── history.html
│
└── manage.py


### **Main Features**
✔ Select a continent  
✔ Retrieve 5 random countries  
✔ Fetch weather for each capital city  
✔ Display results in a table  
✔ Store results to MongoDB  
✔ View history of all searches  

---

## 4. MongoDB Integration

MongoDB is accessed via pymongo:

```python
client = MongoClient("mongodb://<PRIVATE_IP>:27017/")
db = client["assignment10_db"]
collection = db["search_history"]
Each search record includes:

Selected continent

List of results

Date and time of the search

History is retrieved using:

collection.find().sort("created_at", -1).limit(10)

5. Running the Django Server

On the WebServer EC2 instance:

python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000


Then access the app from your browser:

http://<PUBLIC-IP>:8000/

6. Required Screenshots (Assignment Requirements)

Django app showing 5 countries with weather info

MongoDB EC2 instance with mongod running (systemctl status mongod)

Terminal showing JSON records

db.search_history.find().pretty()


EC2 security group inbound rules (WebServer-SG and MongoDB-SG)

7. Technologies Used

Python 3.9+

Django 4.x

MongoDB 7.0

AWS EC2

REST APIs (REST Countries & OpenWeatherMap)

Requests library

Pymongo library

8. Installing Dependencies

Inside the project’s virtual environment:

pip install -r requirements.txt

9. Author

Developed by Petho Tavares for IST105 – Assignment 10.


---

# 📦 **requirements.txt**

```txt
Django==4.2.7
requests==2.31.0
pymongo==4.6.1
