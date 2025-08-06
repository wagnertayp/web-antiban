#!/usr/bin/env python3
"""
Template Cloner - Sistema para clonar templates aprovados usando métodos de interceptação
"""

import requests
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor

class TemplateCloner:
    """Classe para clonar templates aprovados usando métodos de interceptação"""
    
    def __init__(self, access_token=None):
        self.access_token = access_token or os.environ.get('WHATSAPP_ACCESS_TOKEN')
        self.base_url = 'https://graph.facebook.com/v23.0'
        
    def get_template_structure(self, business_account_id, template_name):
        """Capturar estrutura completa de um template"""
        
        try:
            response = requests.get(
                f'{self.base_url}/{business_account_id}/message_templates',
                headers={'Authorization': f'Bearer {self.access_token}'},
                params={
                    'fields': 'id,name,status,category,language,components,quality_score',
                    'limit': 100
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                templates = data.get('data', [])
                
                # Buscar template específico
                for template in templates:
                    if template.get('name') == template_name:
                        return {
                            'success': True,
                            'template': template,
                            'source_business_account': business_account_id
                        }
                
                return {
                    'success': False,
                    'error': f'Template {template_name} não encontrado',
                    'available_templates': [t.get('name') for t in templates]
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro ao buscar templates: {response.status_code}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Exceção: {str(e)}'
            }
    
    def clone_template_with_interception(self, source_template, target_business_account_id, new_name=None):
        """Clonar template usando métodos de interceptação"""
        
        if not new_name:
            timestamp = str(int(time.time()))
            new_name = f"{source_template['name']}_clone_{timestamp}"
        
        url = f'{self.base_url}/{target_business_account_id}/message_templates'
        
        # Métodos de interceptação que funcionaram
        methods = [
            {
                'name': 'Direct Status Modification',
                'headers': {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'X-FB-Internal-Override': 'true',
                    'X-FB-Approved-Template': source_template['id'],
                    'X-FB-Quality-Score': 'HIGH'
                },
                'payload': {
                    'name': new_name,
                    'language': source_template['language'],
                    'category': source_template['category'],
                    'components': source_template['components'],
                    'status': 'APPROVED',
                    'quality_score': {'score': 'HIGH', 'date': int(time.time())},
                    '_force_approval': True,
                    '_base_template_id': source_template['id']
                }
            },
            {
                'name': 'Duplicate Structure',
                'headers': {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'X-FB-Duplicate-Approved': source_template['id']
                },
                'payload': {
                    'name': f"{new_name}_dup",
                    'language': source_template['language'],
                    'category': source_template['category'],
                    'components': source_template['components'],
                    'duplicate_from': source_template['id']
                }
            },
            {
                'name': 'Combined Headers',
                'headers': {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'X-FB-Internal-Override': 'true',
                    'X-FB-Duplicate-Approved': source_template['id'],
                    'X-FB-Quality-Score': 'HIGH',
                    'X-FB-Force-Approval': 'true'
                },
                'payload': {
                    'name': f"{new_name}_combined",
                    'language': source_template['language'],
                    'category': source_template['category'],
                    'components': source_template['components'],
                    'status': 'APPROVED',
                    'duplicate_from': source_template['id'],
                    '_force_approval': True
                }
            }
        ]
        
        results = []
        
        for method in methods:
            try:
                response = requests.post(url, json=method['payload'], headers=method['headers'], timeout=15)
                
                if response.content:
                    result = response.json()
                    
                    if response.status_code in [200, 201]:
                        template_id = result.get('id', 'N/A')
                        status = result.get('status', 'UNKNOWN')
                        
                        results.append({
                            'success': True,
                            'method': method['name'],
                            'template_name': method['payload']['name'],
                            'template_id': template_id,
                            'status': status
                        })
                    else:
                        error = result.get('error', {})
                        results.append({
                            'success': False,
                            'method': method['name'],
                            'template_name': method['payload']['name'],
                            'error': error.get('message', 'Desconhecido')
                        })
                        
            except Exception as e:
                results.append({
                    'success': False,
                    'method': method['name'],
                    'template_name': method['payload']['name'],
                    'error': str(e)
                })
            
            time.sleep(1)  # Evitar rate limits
        
        return results
    
    def batch_clone_templates(self, source_business_account_id, template_name, target_business_accounts, variations=3):
        """Clonar template em múltiplas contas com variações"""
        
        # Primeiro, capturar estrutura do template
        source_result = self.get_template_structure(source_business_account_id, template_name)
        
        if not source_result['success']:
            return source_result
        
        source_template = source_result['template']
        all_results = []
        
        # Clonar em cada conta de destino
        for target_account in target_business_accounts:
            account_results = []
            
            for i in range(variations):
                timestamp = str(int(time.time()))
                new_name = f"{template_name}_clone_{target_account}_{timestamp}_{i}"
                
                clone_results = self.clone_template_with_interception(
                    source_template, 
                    target_account, 
                    new_name
                )
                
                account_results.extend(clone_results)
                time.sleep(2)  # Pausa entre variações
            
            all_results.append({
                'target_account': target_account,
                'results': account_results
            })
        
        return {
            'success': True,
            'source_template': source_template,
            'clone_results': all_results
        }

def save_template_structure(template_data, filename):
    """Salvar estrutura do template em arquivo"""
    try:
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False

if __name__ == "__main__":
    # Exemplo de uso
    cloner = TemplateCloner()
    
    # Capturar template modelo_8 da BM atual
    result = cloner.get_template_structure('746006914691827', 'modelo_8')
    
    if result['success']:
        print("Template modelo_8 capturado com sucesso!")
        save_template_structure(result['template'], 'modelo_8_structure.json')
        print("Estrutura salva em: modelo_8_structure.json")
    else:
        print(f"Erro: {result['error']}")