from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from app.services.document_service import document_service
from app.db.database import get_pool

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Fixed UUID used for all admin/global document uploads
GLOBAL_SESSION_ID = "00000000-0000-0000-0000-000000000000"


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(GLOBAL_SESSION_ID),
):
    try:
        content = await file.read()
        text = await document_service.process_file(file.filename, content)
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
        await document_service.save_document(GLOBAL_SESSION_ID, file.filename, text)
        return {"status": "success", "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_documents():
    documents = await document_service.get_session_documents(GLOBAL_SESSION_ID)
    return {"documents": documents}


@router.post("/reindex")
async def reindex_documents():
    """Re-generate embeddings for all chunks with missing embeddings."""
    result = await document_service.reindex_documents()
    return {"status": "success", **result}


@router.get("/download/{document_id}")
async def download_document(document_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT filename, full_content FROM document_chunks WHERE id = $1 AND full_content IS NOT NULL",
            document_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    base = row["filename"].rsplit(".", 1)[0]
    txt_filename = f"{base}.txt"
    return Response(
        content=row["full_content"].encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{txt_filename}"'},
    )


@router.get("/{session_id}")
async def get_documents(session_id: str):
    documents = await document_service.get_session_documents(GLOBAL_SESSION_ID)
    return {"documents": documents}


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    await document_service.delete_document(document_id)
    return {"status": "success", "message": "Document deleted successfully."}
