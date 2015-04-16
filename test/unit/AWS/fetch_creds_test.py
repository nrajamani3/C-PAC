# test/unit/AWS/fetch_creds_test.py
#
# Contributing authors (please append):
# Daniel Clark

'''
This module performs unit testing on the functions in the
CPAC/AWS/fetch_creds.py module
'''

# Import packages
import unittest
from CPAC.AWS import fetch_creds

# Test case for the run function
class FetchCredsTestCase(unittest.TestCase):
    '''
    This class is a test case for the fetch_creds module

    Inherits
    --------
    unittest.TestCase class

    Attributes (class):
    ------------------
    see unittest.TestCase documentation

    Attributes (instance):
    aws_creds : string
        filepath to the csv file on disk with the AWS credentials
    db_creds : string
        filepath to the csv file on disk with the database login
        credentials
    '''

    # setUp method
    def setUp(self):
        '''
        Method to instantiate input arguments for the
        AWS.fetch_creds() method via instance attributes

        Parameters
        ----------
        self : FetchCredsTestCase
            a unittest.TestCase-inherited class

        Returns
        -------
        None
            this function does not return any values, but populates the
            instance attributes for:
            bucket_name
        '''

        # Init variables
        self.bucket_name = 'fcp-indi'

    # Test getting S3 bucket
    def test_return_bucket(self):
        '''
        Method to test the fetch_creds.return_bucket() function

        Parameters
        ----------
        self : FetchCredsTestCase
            a unittest.TestCase-inherited class

        Returns
        -------
        None
            this function does not return any values, but tests to make
            sure the fetch_creds.return_bucket() function returns a
            bucket object
        '''

        # Import packages
        import boto.s3

        # Init variables
        err_msg = 'Unable to get the S3 bucket!'

        # Grab the AWS bucket
        bucket = fetch_creds.return_bucket(self.bucket_name)

        # Assert that it is a boto bucket object
        self.assertIsInstance(bucket, boto.s3.bucket.Bucket,
                              msg=err_msg)


# Command-line run-able unittest module
if __name__ == '__main__':
    unittest.main()
