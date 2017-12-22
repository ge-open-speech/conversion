import os
from google.cloud import storage
from subprocess import call

storage_client = storage.Client()
bucket_name = 'ge-open-speech-recording.appspot.com'
bucket = storage_client.get_bucket(bucket_name)


def convert():
    blobs = bucket.list_blobs()
    counter = 0
    for blob in blobs:
        just_name = os.path.splitext(blob.name)[0]
        if just_name.startswith("ogg/") or just_name.startswith("wav/"):
            continue
        counter += 1
        if is_converted(blob):
            print("++++Already converted. Deleting.")
            blob.delete()
            print("++++Deleted")
            continue
        print(blob.name)
        ogg_file_name = './ogg/' + blob.name
        blob.download_to_filename(ogg_file_name)
        print("++++Downloaded")
        wav_file_name = './wav/' + just_name + ".wav"
        call(["ffmpeg", "-i", ogg_file_name, wav_file_name])
        print("++++Converted")
        blob_wav_name = 'wav/' + just_name + ".wav"
        blob_wav = storage.Blob(blob_wav_name, bucket)
        blob_wav.upload_from_filename(wav_file_name)
        print("++++Uploaded")
        bucket.copy_blob(blob, bucket, "ogg/" + blob.name)
        print("++++Copied")
        if is_converted(blob):
            print("++++Successfully converted. Deleting.")
            blob.delete()
            print("++++Deleted")
    print(counter)


def is_converted(blob):
    just_name = os.path.splitext(blob.name)[0]
    blob_wav_name = 'wav/' + just_name + ".wav"
    blob_ogg_name = 'ogg/' + just_name + ".ogg"
    ogg_copy_ok = storage.Blob(blob_ogg_name, bucket).exists()
    wav_converted_ok = storage.Blob(blob_wav_name, bucket).exists()
    if ogg_copy_ok and wav_converted_ok:
        return True
    else:
        return False


def restore():
    blobs = bucket.list_blobs(prefix="ogg")
    for blob in blobs:
        just_name = blob.name[4:]
        print(just_name)
        bucket.copy_blob(blob, bucket, just_name)
        blob.delete()


convert()
