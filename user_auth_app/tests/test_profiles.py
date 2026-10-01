from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class RegistrationTests(APITestCase):
    
    
    def test_register_user(self):
        url = reverse('registration')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    
        

class LoginTests(APITestCase):
    
    def test_login_user(self):
        pass
        #url = reverse('login')
           
        
    def test_patch_user_info(self):
            pass