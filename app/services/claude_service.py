# FormatAI/app/services/claude_service.py (VERSÃO CORRIGIDA)

import anthropic
import asyncio
from typing import List, Tuple
from fastapi import UploadFile

from app.core.config import settings

# Inicializa o cliente da Anthropic
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Define as features beta que queremos usar em formato de lista
ACTIVE_BETAS = ["code-execution-2025-08-25", "files-api-2025-04-14"]


async def upload_file_to_claude(file: UploadFile) -> str:
    """Faz o upload de um arquivo para a Files API do Claude e retorna o file_id."""
    print(f"Fazendo upload do arquivo para o Claude: {file.filename}...")
    file_content = await file.read()

    file_tuple = (file.filename, file_content, file.content_type)

    uploaded_file = client.beta.files.upload(file=file_tuple, betas=ACTIVE_BETAS)
    print(f"Upload concluído. File ID: {uploaded_file.id}")
    return uploaded_file.id


def construct_formatting_prompt(source_file_ids: List[dict], template_file_id: dict) -> list:
    """Cria o prompt detalhado para a IA executar a tarefa de formatação."""

    prompt_text = f"""
Você é um assistente especialista em transformação de dados. Sua tarefa é converter os dados dos arquivos de origem para um novo formato, definido por um arquivo de template. Use a ferramenta de execução de código para realizar essa tarefa.

**Instruções Detalhadas:**
1.  **Análise:** Examine o conteúdo e a estrutura de todos os arquivos de origem e do arquivo de template.
2.  **Mapeamento:** Determine a melhor forma de mapear as colunas/dados dos arquivos de origem para as colunas do arquivo de template. Se os nomes forem diferentes (ex: "Valor Total" vs "VLR_TOTAL"), faça o mapeamento de forma inteligente.
3.  **Script Python:** Escreva e execute um script Python usando a biblioteca `pandas` para ler os arquivos de origem, processar os dados e criar um novo DataFrame que corresponda exatamente à estrutura do template. `openpyxl` e `xlrd` estão disponíveis para arquivos Excel. Se encontrar um arquivo .xls (Excel antigo), use `xlrd`. Para .xlsx, use `openpyxl`.
4.  **Consolidação:** Se houver múltiplos arquivos de origem, consolide os dados em um único arquivo de saída.
5.  **Saída:** Salve o resultado final como um arquivo chamado `resultado_formatado.xlsx`. Este nome é obrigatório.
6.  **Conclusão:** Responda apenas com uma mensagem de sucesso curta ao final. O mais importante é a geração do arquivo.
"""

    content_blocks = [{"type": "text", "text": prompt_text}]

    for file_info in source_file_ids:
        content_blocks.append({"type": "container_upload", "file_id": file_info['id']})

    content_blocks.append({"type": "container_upload", "file_id": template_file_id['id']})

    return content_blocks


async def list_claude_files() -> List[dict]:
    """Lista todos os arquivos no workspace do Claude e os organiza."""
    print("Buscando lista de arquivos do Claude...")
    files_list = client.beta.files.list(betas=ACTIVE_BETAS)

    processed_files = []
    for file in files_list.data:
        processed_files.append({
            "id": file.id,
            "filename": file.filename,
            "size": file.size_bytes,
            "created_at": file.created_at,
            "downloadable": file.downloadable
        })

    # Ordena por data de criação, os mais recentes primeiro
    processed_files.sort(key=lambda x: x['created_at'], reverse=True)
    print(f"Encontrados {len(processed_files)} arquivos.")
    return processed_files


# Também vamos precisar de uma forma de pegar os metadados de um arquivo existente
async def get_file_metadata(file_id: str) -> dict:
    """Busca os metadados de um arquivo específico pelo seu ID."""
    print(f"Buscando metadados para o arquivo: {file_id}")
    metadata = client.beta.files.retrieve_metadata(file_id, betas=ACTIVE_BETAS)
    return {"id": metadata.id, "filename": metadata.filename}


async def request_data_transformation(
        new_source_files: List[UploadFile],
        new_template_file: UploadFile,
        existing_source_ids: List[str],
        existing_template_id: str
) -> Tuple[bytes, str]:
    """
    Orquestra o processo, aceitando uma mistura de novos arquivos e IDs existentes.
    """
    all_source_files_info = []

    # 1. Processa novos uploads de origem
    if new_source_files:
        upload_tasks = [upload_file_to_claude(f) for f in new_source_files]
        results = await asyncio.gather(*upload_tasks)
        for res, f in zip(results, new_source_files):
            all_source_files_info.append({'id': res, 'filename': f.filename})

    # 2. Processa IDs de origem existentes
    if existing_source_ids:
        metadata_tasks = [get_file_metadata(id) for id in existing_source_ids]
        metadata_results = await asyncio.gather(*metadata_tasks)
        all_source_files_info.extend(metadata_results)

    # 3. Processa o template
    template_file_info = {}
    if new_template_file:
        template_id = await upload_file_to_claude(new_template_file)
        template_file_info = {'id': template_id, 'filename': new_template_file.filename}
    elif existing_template_id:
        template_file_info = await get_file_metadata(existing_template_id)

    if not all_source_files_info or not template_file_info:
        raise ValueError("É necessário fornecer pelo menos um arquivo de origem e um arquivo de template.")

    # O resto da função continua como antes...
    prompt_content = construct_formatting_prompt(all_source_files_info, template_file_info)

    print("Enviando requisição de formatação para o Claude...")
    response = client.beta.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": prompt_content
        }],
        tools=[{
            "type": "code_execution_20250825",
            "name": "code_execution"
        }],
        betas=ACTIVE_BETAS
    )
    print("Claude processou a requisição. Analisando a resposta...")

    output_file_id = None
    for item in response.content:
        if item.type == 'bash_code_execution_tool_result':
            content_item = item.content
            if content_item.type == 'bash_code_execution_result':
                for block in content_item.content:
                    if block.type == 'bash_code_execution_output_file' and block.filename == 'resultado_formatado.xlsx':
                        output_file_id = block.file_id
                        break
        if output_file_id:
            break

    if not output_file_id:
        error_message = "Não foi possível encontrar o arquivo de saída 'resultado_formatado.xlsx' gerado pela IA."
        text_blocks = [block.text for block in response.content if block.type == 'text']
        if text_blocks:
            error_message += f" Resposta do Claude: {' '.join(text_blocks)}"
        print("Estrutura da resposta do Claude:", response.content)
        raise Exception(error_message)

    print(f"Arquivo de resultado encontrado: {output_file_id}")

    print("Fazendo download do arquivo formatado...")
    file_metadata = client.beta.files.retrieve_metadata(output_file_id, betas=ACTIVE_BETAS)
    file_content_stream = client.beta.files.download(output_file_id, betas=ACTIVE_BETAS)

    return file_content_stream.read(), file_metadata.filename