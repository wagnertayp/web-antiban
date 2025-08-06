# Templates Neutros para Criar

## Como criar templates neutros e aprovables

Quando a API estiver disponível (sem rate limit), use estes comandos para criar templates totalmente neutros:

### Template 1: aviso_geral (Português)
```bash
curl -X POST https://graph.facebook.com/v23.0/746006914691827/message_templates \
-H "Authorization: Bearer SEU_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "name": "aviso_geral",
  "language": "pt_BR", 
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Olá {{1}}, temos uma informação importante para você sobre {{2}}. Entre em contato para mais detalhes."
    }
  ]
}'
```

### Template 2: info_update (Inglês)
```bash
curl -X POST https://graph.facebook.com/v23.0/746006914691827/message_templates \
-H "Authorization: Bearer SEU_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "name": "info_update",
  "language": "en", 
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hello {{1}}, we have an important update for you regarding {{2}}. Please contact us for more details."
    }
  ]
}'
```

### Template 3: mensagem_informativa (Português Simples)
```bash
curl -X POST https://graph.facebook.com/v23.0/746006914691827/message_templates \
-H "Authorization: Bearer SEU_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "name": "mensagem_informativa",
  "language": "pt_BR", 
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Olá {{1}}, temos uma informação para você sobre {{2}}. Obrigado pela atenção."
    }
  ]
}'
```

## Características dos Templates

- **Categoria**: UTILITY (aprovação mais rápida)
- **Conteúdo**: Totalmente neutro, sem referências específicas
- **Variáveis**: {{1}} = Nome, {{2}} = Documento/Informação
- **Sem botões**: Templates simples sem componentes complexos
- **Linguagem**: Profissional mas amigável

## Sistema Já Configurado

O sistema já está preparado para usar estes templates quando estiverem aprovados:
- Detecção automática do erro #135000
- Fallback inteligente para BMs com dropdown
- Suporte universal para qualquer template aprovado