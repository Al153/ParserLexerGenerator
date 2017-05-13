getWeather("Google")>>filter(x:(x.temperature>15))>>map(x:{message=("it's going to be %0 degreesToday").format(x.temperature)})>>Email("al@altaylor.io")

