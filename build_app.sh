git add .
git commit -m "$1"
git push origin -u main:main
docker build -t palondomus/geniewishbackend:latest .
docker push palondomus/geniewishbackend:latest 
docker run -it -p 8080:8080 palondomus/geniewishbackend:latest