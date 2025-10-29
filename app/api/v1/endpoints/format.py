# Substitua o conteúdo de app/api/v1/endpoints/format.py por este

from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import io

from app.services import claude_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_upload_form(request: Request):
    """Serve a página HTML principal."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/files", tags=["Files"])
async def list_files():
    """Endpoint para o frontend buscar a lista de arquivos do Claude."""
    try:
        files = await claude_service.list_claude_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/formatar", tags=["Formatting"])
async def format_files(
    # Novos arquivos
    source_files: List[UploadFile] = File([], description="Um ou mais novos arquivos de origem"),
    template_file: Optional[UploadFile] = File(None, description="Um novo arquivo de modelo"),
    # IDs de arquivos existentes, enviados pelo formulário
    existing_source_ids: List[str] = Form([], description="IDs de arquivos de origem existentes"),
    existing_template_id: Optional[str] = Form(None, description="ID de um arquivo de template existente")
):
    """
    Recebe uma mistura de novos arquivos e IDs existentes, envia para formatação
    e retorna o arquivo processado para download.
    """
    try:
        # Validação: Garante que pelo menos um template (novo ou existente) foi fornecido
        if not template_file and not existing_template_id:
            raise HTTPException(status_code=400, detail="Você deve fornecer um arquivo de template (novo ou existente).")
        if template_file and existing_template_id:
            raise HTTPException(status_code=400, detail="Forneça apenas um template, seja um novo upload ou um existente, não ambos.")

        result_content, result_filename = await claude_service.request_data_transformation(
            new_source_files=source_files,
            new_template_file=template_file,
            existing_source_ids=existing_source_ids,
            existing_template_id=existing_template_id
        )

        return StreamingResponse(
            io.BytesIO(result_content),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{result_filename}"'}
        )

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")