import sqlite3
import StringIO

from flask_restful import Resource, reqparse, abort
from flask_jwt import jwt_required

from boto.s3.connection import S3Connection

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
FILE_CONTENT_TYPES = { # these will be used to set the content type of S3 object. It is binary by default.
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}
AWS_ACCESS_KEY_ID = 'aws-access-key-id'
AWS_SECRET_ACCESS_KEY = 'aws-secret-access-key'

class ImageFile(Resource):

    parser = reqparse.RequestParser(argument_class=FileStorageArgument)
    parser.add_argument('image', required=True, type=FileStorage, location='files')

    @jwt_required()
    def put(self):
        #TODO: a check on file size needs to be there.

        args = self.parser.parse_args()
        image = args['image']

        # check logo extension
        extension = image.filename.rsplit('.', 1)[1].lower()
        if '.' in image.filename and not extension in ALLOWED_EXTENSIONS:
            abort(400, message="File extension is not one of our supported types.")

        # create a file object of the image
        image_file = StringIO()
        image.save(image_file)

        # upload to s3
        key_name = '{0}.{1}'.format('some-name', extension)
        content_type = FILE_CONTENT_TYPES[extension]
        bucket_name = 'some-bucket-name'
        logo_url = upload_s3(image_file, key_name, content_type, bucket_name)

        return {'logo_url': logo_url}

    @jwt_required
    def get(self):
        args = self.parser.parse_args()
        image = args['image']

def upload_s3(file, key_name, content_type, bucket_name):
    """Uploads a given StringIO object to S3. Closes the file after upload.
    Returns the URL for the object uploaded.
    Note: The acl for the file is set as 'public-acl' for the file uploaded.
    Keyword Arguments:
    file -- StringIO object which needs to be uploaded.
    key_name -- key name to be kept in S3.
    content_type -- content type that needs to be set for the S3 object.
    bucket_name -- name of the bucket where file needs to be uploaded.
    """
    # create connection
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    # upload the file after getting the right bucket
    bucket = conn.get_bucket(bucket_name)
    obj = S3Key(bucket)
    obj.name = key_name
    obj.content_type = content_type
    obj.set_contents_from_string(file.getvalue())
    obj.set_acl('public-read')

    # close stringio object
    file.close()

    return obj.generate_url(expires_in=0, query_auth=False)


class FileStorageArgument(reqparse.Argument):
    """
        This argument class for flask-restful will be used in
        all cases where file uploads need to be handled.
    """

    def convert(self, value, op):
        if self.type is FileStorage:  # only in the case of files
            # this is done as self.type(value) makes the name attribute of the
            # FileStorage object same as argument name and value is a FileStorage
            # object itself anyways
            return value

        # called so that this argument class will also be useful in
        # cases when argument type is not a file.
        super(FileStorageArgument, self).convert(*args, **kwargs)
