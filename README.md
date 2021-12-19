# optimal-transport

[![CircleCI](https://circleci.com/gh/chdefrene/optimal-transport/tree/main.svg?style=svg&circle-token=fa5efbf41b545a386450c21e482ad4dd6f105fa3)](https://circleci.com/gh/chdefrene/optimal-transport/)

## Case solution for Ur Solutions

This application will calculate an optimal route from Optimal Transport HQ (Edvard Storms gate 2) to a destination of your choice, while taking into account the local weather conditions along the route.

The main functionality behaves this way:
* Calculate a route between Optimal Transport HQ and the destination.
* Divide the route into 30 km intervals, and store their geo coordinates.
* Fetch a weather report for each geo point from the previous step. Account for the time it takes before the car reaches this point, i.e. if it takes 2 hours to reach, a weather forecast 2 hours in the future should be used.
* Calculate a delay if weather condition matches one of the conditions we are aware of. If there are multiple weather conditions, any delays are aggregated.
* Sum up all weather related delays, and apply them to the original route estimate.

I have selected 3 external APIs to solve this assignment:
1. [TomTom](https://developer.tomtom.com) for map routing functionality. The API provides generous access with 2500 daily route plans, and provides geo-points for all instructions along the route
2. [OpenWeather](https://openweathermap.org/api) for weather reports. The API provides 60 free API calls per minute, which is enough to cover trips up to 30 km * 60 = 1800 km without having to wait. The API also provides both current weather and hourly forcasts, which makes it more accurate to plan for upcoming local weather along the route.
3. [Geopy](https://pypi.org/project/geopy/) for translating addresses into geo coordinates. The application felt a bit more human-friendly when not having to input geo coordinates all the time.

The two first integrations have been split up into different business logic, and have unit tests written for them, including mocked API calls. A CircleCI configuration runs all tests for every push to this repo.

## Using the app

The app is hosted at Vercel on this URL: https://optimal-transport.vercel.app/api/route

I have used the [Flask framework](https://flask.palletsprojects.com/en/2.0.x/) to provide API routes for the business logic, and I host it as a [WSGI application](https://vercel.com/docs/runtimes#advanced-usage/advanced-python-usage/web-server-gateway-interface) using Vercel's Python runtime. 

To access it, send a POST request including this data object:
```
{
  "address": "<YOUR DESTINATION OF CHOICE>"
}
```

Due to time constraints I have not been able to create a frontend for this task. A simple solution would be to create a static HTML page containing an input field for the address, and a submit button that redirects to the URL above.

<img width="1138" alt="Skjermbilde 2021-12-20 kl  00 20 30" src="https://user-images.githubusercontent.com/6738930/146694624-f01c5bfd-9628-46b1-b12c-d9fe5fdf36b8.png">

