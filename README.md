# Photo Editr [![Travis build badge](https://travis-ci.org/andela-osule/photo-editing-application.svg?branch=master)](https://travis-ci.org/andela-osule/photo-editing-application) [![Coverage Status](https://coveralls.io/repos/andela-osule/photo-editing-application/badge.svg?branch=master&service=github)](https://coveralls.io/github/andela-osule/photo-editing-application?branch=master)
A photo editor for happy people powered by Django.
--------------------------------------------------
Photo Editr allows you to edit your photos and share them with your friends.

Features include `social authentication with facebook`, `about 18 available filters and effects`, `photo sharing to your social feeds`.

### Dependencies
Some awesome projects worthy of mention without which this application would have been one heck of a task fit for Hercule himself.
- [facebook-sdk](https://github.com/pythonforfacebook/facebook-sdk)
- [Pillow](https://github.com/python-pillow/Pillow)
- [bootstrap](https://github.com/twbs/bootstrap)
- [font-awesome](https://github.com/FortAwesome/Font-Awesome)
- [jquery](https://github.com/jquery/jquery)
- [angular](https://github.com/angular/angular)
- [angular-animate](https://github.com/angular/animate)
- [angular-moment](https://github.com/urish/angular-moment)
- [angular-slick-carousel](https://github.com/devmark/angular-slick-carousel)
- [ng-file-upload](https://github.com/danialfarid/ng-file-upload)

### First Things, First
You should do an install of all package requirements in your python setup or go about creating a virtual environment.

Clone this repository
```bash
git clone https://github.com/andela-osule/photo-editing-application.git & cd photo-editing-application
```
Install the requirements
```bash
pip install -r requirements.txt
```
Create database tables and migrate
```bash
python photo_editor/manage.py bower install -- -s
python photo_editor/manage.py collectstatic --noinput
python photo_editor/manage.py makemigrations
python photo_editor/manage.py migrate
```

### How To Start The Server
Run the following command to start the server and begin listening for requests to each endpoints.
```bash
python photo_editor/manage.py runserver
```

### Available Filters
- Basic
    - Alien
    - Blur
    - Blur More
    - Brighten
    - Contour
    - Detail
    - Edge
    - Edge Enhance
    - Edge Enhance More
    - Emboss
    - Find Edges
    - Smooth
    - Smooth More
    - Sharpen
    - Sharpen More
- Advanced
    - Sepia
    - Whoops
    - Grayscale

More filters are on the way.

### Contribution
Send a pull request and brew coffee. I shall look through it and do the needful.
