#!/usr/bin/python3
''' module for file_storage tests '''
from io import StringIO
import os
import unittest
from unittest.mock import patch
import MySQLdb
from console import HBNBCommand
from models.user import User
from models import storage
from datetime import datetime


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db',
                 'file_storage test not supported here')
class TestDBStorageWithConsole(unittest.TestCase):
    """
    Test dbstorage engine with console
    """
    def query(self, string):
        """Sending database query"""
        db = MySQLdb.connect(
            user=os.getenv('HBNB_MYSQL_USER'),
            host=os.getenv('HBNB_MYSQL_HOST'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            port=int(os.getenv('HBNB_MYSQL_PORT')),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cur = db.cursor()
        cur.execute(string)
        count = cur.fetchall()
        cur.close()
        db.close()
        return count

    def test_create_state(self):
        """Test create State"""
        string = "SELECT * FROM states"
        old_count = self.query(string)
        cmd = 'create State name="California"'
        self.getOutput(cmd)
        new_count = self.query(string)
        self.assertEqual(len(new_count) - len(old_count), 1)

    def getOutput(self, command):
        """Get output from stdout"""
        with patch('sys.stdout', new=StringIO()) as out:
            cmd = HBNBCommand()
            cmd.onecmd(command)
            return out.getvalue().strip()

    def test_create_place_with_integer_and_float(self):
        """Test create City"""
        string = "SELECT * FROM places"
        # old_count = self.query(string)
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "San_Francisco_is_super_cool"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        city_id = self.getOutput(cmd)
        cmd = f'create User email="my@me.com"\
            password="pwd" first_name="FN" last_name="LN"'
        user_id = self.getOutput(cmd)
        cmd = f'create Place city_id="{city_id}" user_id="{user_id}"\
            name="My_house" description="no_description_yet" number_rooms=4\
            number_bathrooms=1 max_guest=3 price_by_night=100 latitude=120.12\
            longitude=101.4'
        place_id = self.getOutput(cmd)
        new_count = self.query(string)
        self.assertIn(place_id, str(new_count))
        self.assertIn('100', str(new_count))
        self.assertIn('120.12', str(new_count))

    def test_create_city_with_underscore(self):
        """Test create City"""
        string = "SELECT * FROM cities"
        old_count = self.query(string)
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "San_Francisco_is_super_cool"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        city_id = self.getOutput(cmd)
        new_count = self.query(string)
        self.assertEqual(len(new_count) - len(old_count), 1)
        cmd = 'show City {}'.format(city_id)
        output = self.getOutput(cmd)
        self.assertIn(name.replace('_', ' '), output)

    def test_create_city_without_underscore(self):
        """Test create City"""
        string = "SELECT * FROM cities"
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "Fremont"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        self.getOutput(cmd)
        new_count = self.query(string)
        self.assertIn(name.replace('_', ' '), str(new_count))


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db',
                 'db_storage test not supported')
class TestDBStorage(unittest.TestCase):
    '''testing dbstorage engine'''

    def test_new_and_save(self):
        '''testing  the new and save methods'''
        db = MySQLdb.connect(user=os.getenv('HBNB_MYSQL_USER'),
                             host=os.getenv('HBNB_MYSQL_HOST'),
                             passwd=os.getenv('HBNB_MYSQL_PWD'),
                             port=3306,
                             db=os.getenv('HBNB_MYSQL_DB'))
        new_user = User(**{'first_name': 'jack',
                           'last_name': 'bond',
                           'email': 'jack@bond.com',
                           'password': 12345})
        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM users')
        old_count = cur.fetchall()
        cur.close()
        db.close()
        new_user.save()
        db = MySQLdb.connect(user=os.getenv('HBNB_MYSQL_USER'),
                             host=os.getenv('HBNB_MYSQL_HOST'),
                             passwd=os.getenv('HBNB_MYSQL_PWD'),
                             port=3306,
                             db=os.getenv('HBNB_MYSQL_DB'))
        cur = db.cursor()
        cur.execute('SELECT COUNT(*) FROM users')
        new_count = cur.fetchall()
        self.assertEqual(new_count[0][0], old_count[0][0] + 1)
        cur.close()
        db.close()

    def test_new(self):
        """ New object is correctly added to database """
        new = User(
            email='john2020@gmail.com',
            password='password',
            first_name='John',
            last_name='Zoldyck'
        )
        self.assertFalse(new in storage.all().values())
        new.save()
        self.assertTrue(new in storage.all().values())
        dbc = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST'),
            port=3306,
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cursor = dbc.cursor()
        cursor.execute('SELECT * FROM users WHERE id="{}"'.format(new.id))
        result = cursor.fetchone()
        self.assertTrue(result is not None)
        self.assertIn('john2020@gmail.com', result)
        self.assertIn('password', result)
        self.assertIn('John', result)
        self.assertIn('Zoldyck', result)
        cursor.close()
        dbc.close()

    def test_delete(self):
        """ Object is correctly deleted from database """
        new = User(
            email='john2020@gmail.com',
            password='password',
            first_name='John',
            last_name='Zoldyck'
        )
        obj_key = 'User.{}'.format(new.id)
        dbc = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST'),
            port=3306,
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        new.save()
        self.assertTrue(new in storage.all().values())
        cursor = dbc.cursor()
        cursor.execute('SELECT * FROM users WHERE id="{}"'.format(new.id))
        result = cursor.fetchone()
        self.assertTrue(result is not None)
        self.assertIn('john2020@gmail.com', result)
        self.assertIn('password', result)
        self.assertIn('John', result)
        self.assertIn('Zoldyck', result)
        self.assertIn(obj_key, storage.all(User).keys())
        new.delete()
        self.assertNotIn(obj_key, storage.all(User).keys())
        cursor.close()
        dbc.close()

    def test_reload(self):
        """ Tests the reloading of the database session """
        dbc = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST'),
            port=3306,
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cursor = dbc.cursor()
        cursor.execute(
            'INSERT INTO users(id, created_at, updated_at, email, password' +
            ', first_name, last_name) VALUES(%s, %s, %s, %s, %s, %s, %s);',
            [
                '4447-r4n4-6u11s',
                str(datetime.now()),
                str(datetime.now()),
                'lewl@yahoo.com',
                'pass',
                'Fwyd',
                'Be',
            ]
        )
        self.assertNotIn('User.4447-r4n4-6u11s', storage.all())
        dbc.commit()

        storage.reload()
        self.assertIn('User.4447-r4n4-6u11s', storage.all())
        cursor.close()
        dbc.close()

    def test_save(self):
        """ object is successfully saved to database """
        new = User(
            email='john2020@gmail.com',
            password='password',
            first_name='John',
            last_name='Zoldyck'
        )
        dbc = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST'),
            port=3306,
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cursor = dbc.cursor()
        cursor.execute('SELECT * FROM users WHERE id="{}"'.format(new.id))
        result = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM users;')
        old_cnt = cursor.fetchone()[0]
        self.assertTrue(result is None)
        self.assertFalse(new in storage.all().values())
        new.save()
        dbc1 = MySQLdb.connect(
            host=os.getenv('HBNB_MYSQL_HOST'),
            port=3306,
            user=os.getenv('HBNB_MYSQL_USER'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cursor1 = dbc1.cursor()
        cursor1.execute('SELECT * FROM users WHERE id="{}"'.format(new.id))
        result = cursor1.fetchone()
        cursor1.execute('SELECT COUNT(*) FROM users;')
        new_cnt = cursor1.fetchone()[0]
        self.assertFalse(result is None)
        self.assertEqual(old_cnt + 1, new_cnt)
        self.assertTrue(new in storage.all().values())
        cursor1.close()
        dbc1.close()
        cursor.close()
        dbc.close()
