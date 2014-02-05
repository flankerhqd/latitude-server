from django.contrib.auth.models import User
from django.test import TestCase
import datetime
from rest_framework.test import APIRequestFactory, APIClient
from django.core.urlresolvers import reverse
from rest_framework import status
from latitudeapi.models import Location,FriendShip
from rest_framework.test import APITestCase
# Create your tests here.
class UserRegisterTestCase(APITestCase):
    '''
    test creating account
    '''
    def test_create_account(self):
        url = reverse('user-list')
        data = {'username':'test',
                'password':'test',
                'email':'test@test.com'
        }
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        del data['password']
        del response.data['id']
        self.assertDictEqual(response.data, data)

class UserLoginTestCase(APITestCase):
    '''
    test user can login
    '''
    def setUp(self):
        User.objects.create_user(username="test",password="test",email="test@test.com")
    def test_can_login(self):
        url = reverse('user-login')
        data = {'username':'test','password':'test'}
        response = self.client.post(url,data,format = 'json')
        #we should get a response of {"token": "xxxx"}
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.status_code,status.HTTP_200_OK)

        #test token is meaningful
        token = response.data['token']
        #add Authorization: Token xxxx to your request header

        client = APIClient()
        #client.login(username='test',password='test')
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        #user should be able to get his locations
        response = client.get(reverse('location-list'))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),0)

class UserFriendTestCase(APITestCase):
    '''
    test user-friend interaction
    '''
    def setUp(self):
        User.objects.create_user(username="test1",password="test",email="test1@test.com")
        User.objects.create_user(username="test2",password="test",email="test2@test.com")

    def test_add_friend(self):
        url = reverse('friendship-list')
        data = {'to_friend':"test1"}

        client = APIClient()
        client.login(username = "test2", password = "test")
        response = client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictContainsSubset(data, response.data)

        response = client.get(url,format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['to_friend'],"test1")

        data = {'to_friend':"test2"}
        response = client.post(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLocationFetchTestCase(APITestCase):
    '''
    test user-location functions
    '''
    def setUp(self):
        user1 = User.objects.create_user(username="test1",password="test",email="test1@test.com")
        user2 = User.objects.create_user(username="test2",password="test",email="test2@test.com")
        user3 = User.objects.create_user(username="test3",password="test",email="test3@test.com")
        user4 = User.objects.create_user(username="test4",password="test",email="test3@test.com")
        FriendShip(from_friend=user1, to_friend=user2).save()
        FriendShip(from_friend=user1, to_friend=user3).save()
        Location.objects.create(owner=user1, lat=1.0, lon=5.0,prec=7.0,ts=datetime.datetime.now())
        Location.objects.create(owner=user2, lat=2.0, lon=2.0,prec=2.0,ts=datetime.datetime.now())
        Location.objects.create(owner=user2, lat=3.0, lon=3.0,prec=3.0,ts=datetime.datetime.now())
        Location.objects.create(owner=user4, lat=0.0, lon=0.0,prec=0.0,ts=datetime.datetime.now())

    def test_fetch_location(self):
        '''
        get user's self location history
        '''
        client = APIClient()
        client.login(username = "test1", password = "test")
        response = client.get(reverse('location-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['lat'], 1.0)
        self.assertEqual(response.data[0]['lon'], 5.0)
        self.assertEqual(response.data[0]['prec'], 7.0)

        client.login(username = "test2", password = "test")
        response = client.get(reverse('location-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)

        self.assertEqual(response.data[0]['lat'], 3.0)
        self.assertEqual(response.data[0]['lon'], 3.0)
        self.assertEqual(response.data[0]['prec'], 3.0)

        self.assertEqual(response.data[1]['lat'], 2.0)
        self.assertEqual(response.data[1]['lon'], 2.0)
        self.assertEqual(response.data[1]['prec'], 2.0)

    def test_add_location(self):
        client = APIClient()
        client.login(username = 'test3', password = 'test')
        url = reverse('location-list')
        data = {
            'lat':5,
            'lon':5,
            'prec':5,
            'ts':str(datetime.datetime.now())
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['lat'], 5.0)
        self.assertEqual(response.data['lon'], 5.0)
        self.assertEqual(response.data['prec'], 5.0)

        response = client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),1)

        self.assertEqual(response.data[0]['lat'], 5.0)
        self.assertEqual(response.data[0]['lon'], 5.0)
        self.assertEqual(response.data[0]['prec'], 5.0)

    def test_get_friend_location(self):
        '''
        notice friend without location will *not* be listed in response
        '''
        client = APIClient()
        client.login(username='test1',password='test')
        url = reverse('friend-location')
        response = client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #because user3 does not have a location
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['owner'], 'test2')






