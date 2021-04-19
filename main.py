import shutil
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

import aeneas.globalconstants as gc
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.task import Task, TaskConfiguration
from aeneas.textfile import TextFileFormat

LanguageEnum = Enum("Language", zip(Language.ALLOWED_VALUES, Language.ALLOWED_VALUES), type=str)
TextFileFormatEnum = Enum("TextFileFormat", zip(TextFileFormat.ALLOWED_VALUES, TextFileFormat.ALLOWED_VALUES), type=str)


class Message500(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "detail": "Error during processing",
            },
        }


def convert_to_tempfile(file: UploadFile) -> NamedTemporaryFile:
    """
    Convert UploadFile to named temporary file. 
    !!! Closes the UploadFile
    """
    try:
        file.file.seek(0)
        suffix = Path(file.filename).suffix
        tmp_file = NamedTemporaryFile(suffix=suffix)
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file.seek(0)
    finally:
        file.file.close()
    return tmp_file




app = FastAPI()


@app.post(
    "/",
    response_model=list[tuple[str, str, str]],
    responses={
        200: {"model": list[tuple[str, str, str]]},
        500: {"model": Message500},
    },
)
def align_audio(
    language: LanguageEnum = Form(...), text_file_format: TextFileFormatEnum = Form(...), transcript: UploadFile = File(...), audio: UploadFile = File(...),
):  
    try:
        # prepare config
        aeneas_config = TaskConfiguration()
        aeneas_config[gc.PPN_TASK_IS_TEXT_FILE_FORMAT] = text_file_format
        aeneas_config[gc.PPN_TASK_LANGUAGE] = language
        
        # get named temporary files
        tmp_audio = convert_to_tempfile(audio)
        tmp_transcript = convert_to_tempfile(transcript)

        # create task
        task = Task()
        task.configuration = aeneas_config
        task.audio_file_path_absolute = Path(tmp_audio.name)
        task.text_file_path_absolute = Path(tmp_transcript.name)
        
        # process Task
        ExecuteTask(task).execute()

        tmp_audio.close()
        tmp_transcript.close()

        return [(str(fragment.begin), str(fragment.end), fragment.text) for fragment in task.sync_map_leaves() if fragment.is_regular]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error during processing: " + str(e)
        ) from e
