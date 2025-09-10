#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para unir arquivos Excel (.xls, .xlsx) e CSV em um único arquivo.

O script solicita ao usuário:
1. O caminho da pasta onde estão os arquivos
2. A seleção dos arquivos na ordem desejada
3. Une os arquivos mantendo apenas o cabeçalho do primeiro
4. Salva o resultado como 'unidos.xlsx'
"""

import os
import pandas as pd
from pathlib import Path


def listar_arquivos_suportados(pasta):
    """
    Lista todos os arquivos .xls, .xlsx e .csv na pasta especificada.
    
    Args:
        pasta (str): Caminho para a pasta
        
    Returns:
        list: Lista de arquivos suportados encontrados
    """
    extensoes_suportadas = ['.xls', '.xlsx', '.csv']
    arquivos = []
    
    try:
        pasta_path = Path(pasta)
        if not pasta_path.exists():
            return []
            
        for arquivo in pasta_path.iterdir():
            if arquivo.is_file() and arquivo.suffix.lower() in extensoes_suportadas:
                arquivos.append(arquivo.name)
                
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        return []
    
    return sorted(arquivos)


def ler_arquivo(caminho_arquivo):
    """
    Lê um arquivo Excel ou CSV e retorna um DataFrame.
    
    Args:
        caminho_arquivo (str): Caminho completo para o arquivo
        
    Returns:
        pandas.DataFrame: DataFrame com os dados do arquivo
    """
    try:
        extensao = Path(caminho_arquivo).suffix.lower()
        
        if extensao == '.csv':
            # Tenta diferentes encodings para CSV
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(caminho_arquivo, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # Se nenhum encoding funcionou, usa o padrão
            return pd.read_csv(caminho_arquivo)
            
        elif extensao in ['.xls', '.xlsx']:
            return pd.read_excel(caminho_arquivo)
            
        else:
            raise ValueError(f"Formato de arquivo não suportado: {extensao}")
            
    except Exception as e:
        print(f"Erro ao ler arquivo {caminho_arquivo}: {e}")
        return None


def obter_pasta_usuario():
    """
    Solicita ao usuário o caminho da pasta e valida se existe.
    
    Returns:
        str: Caminho válido da pasta ou None se cancelado
    """
    while True:
        pasta = input("\nDigite o caminho da pasta onde estão os arquivos: ").strip()
        
        if not pasta:
            print("Caminho não pode estar vazio.")
            continue
            
        pasta_path = Path(pasta)
        
        if not pasta_path.exists():
            print(f"Pasta não encontrada: {pasta}")
            resposta = input("Deseja tentar novamente? (s/n): ").strip().lower()
            if resposta != 's':
                return None
            continue
            
        if not pasta_path.is_dir():
            print(f"O caminho especificado não é uma pasta: {pasta}")
            resposta = input("Deseja tentar novamente? (s/n): ").strip().lower()
            if resposta != 's':
                return None
            continue
            
        return str(pasta_path.absolute())


def selecionar_arquivos(arquivos):
    """
    Permite ao usuário selecionar arquivos na ordem desejada.
    
    Args:
        arquivos (list): Lista de arquivos disponíveis
        
    Returns:
        list: Lista de arquivos selecionados na ordem escolhida
    """
    if not arquivos:
        print("Nenhum arquivo suportado encontrado na pasta.")
        return []
    
    print(f"\nArquivos disponíveis:")
    for i, arquivo in enumerate(arquivos, 1):
        print(f"{i}. {arquivo}")
    
    arquivos_selecionados = []
    arquivos_disponiveis = arquivos.copy()
    
    print("\nSelecione os arquivos digitando o número correspondente.")
    print("Pressione ENTER sem digitar nada para finalizar a seleção.")
    
    while arquivos_disponiveis:
        try:
            entrada = input(f"\nEscolha um arquivo (1-{len(arquivos_disponiveis)}) ou ENTER para finalizar: ").strip()
            
            if not entrada:
                break
                
            indice = int(entrada) - 1
            
            if 0 <= indice < len(arquivos_disponiveis):
                arquivo_selecionado = arquivos_disponiveis[indice]
                arquivos_selecionados.append(arquivo_selecionado)
                arquivos_disponiveis.remove(arquivo_selecionado)
                
                print(f"✓ Adicionado: {arquivo_selecionado}")
                
                if arquivos_disponiveis:
                    print("\nArquivos restantes:")
                    for i, arquivo in enumerate(arquivos_disponiveis, 1):
                        print(f"{i}. {arquivo}")
                else:
                    print("\nTodos os arquivos foram selecionados.")
                    break
            else:
                print(f"Número inválido. Digite um número entre 1 e {len(arquivos_disponiveis)}.")
                
        except ValueError:
            print("Por favor, digite um número válido ou pressione ENTER para finalizar.")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return []
    
    return arquivos_selecionados


def unir_arquivos(pasta, arquivos_selecionados):
    """
    Une os arquivos selecionados em um único DataFrame.
    
    Args:
        pasta (str): Caminho da pasta onde estão os arquivos
        arquivos_selecionados (list): Lista de arquivos para unir
        
    Returns:
        pandas.DataFrame: DataFrame com todos os dados unidos
    """
    if not arquivos_selecionados:
        return None
    
    dataframes = []
    primeiro_arquivo = True
    
    print(f"\nProcessando {len(arquivos_selecionados)} arquivo(s)...")
    
    for arquivo in arquivos_selecionados:
        caminho_completo = os.path.join(pasta, arquivo)
        print(f"Lendo: {arquivo}")
        
        df = ler_arquivo(caminho_completo)
        
        if df is None:
            print(f"Erro ao ler {arquivo}. Pulando...")
            continue
            
        if df.empty:
            print(f"Arquivo {arquivo} está vazio. Pulando...")
            continue
        
        # Remove o cabeçalho de todos os arquivos exceto o primeiro
        if not primeiro_arquivo:
            # Se o primeiro arquivo tem cabeçalho, remove a primeira linha dos demais
            if len(df) > 0:
                df = df.iloc[1:].reset_index(drop=True)
        
        dataframes.append(df)
        primeiro_arquivo = False
        print(f"✓ {arquivo}: {len(df)} linhas processadas")
    
    if not dataframes:
        print("Nenhum arquivo válido foi processado.")
        return None
    
    # Une todos os DataFrames
    resultado = pd.concat(dataframes, ignore_index=True)
    print(f"\n✓ Total de linhas no arquivo final: {len(resultado)}")
    
    return resultado


def salvar_arquivo_final(pasta, df_resultado):
    """
    Salva o DataFrame resultado como 'unidos.xlsx' na pasta especificada.
    
    Args:
        pasta (str): Caminho da pasta onde salvar
        df_resultado (pandas.DataFrame): DataFrame para salvar
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        caminho_saida = os.path.join(pasta, 'unidos.xlsx')
        df_resultado.to_excel(caminho_saida, index=False)
        print(f"✓ Arquivo salvo com sucesso: {caminho_saida}")
        return True
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return False


def main():
    """
    Função principal do script.
    """
    print("=" * 50)
    print("  SCRIPT PARA UNIR ARQUIVOS EXCEL E CSV")
    print("=" * 50)
    
    # 1. Obter pasta do usuário
    pasta = obter_pasta_usuario()
    if not pasta:
        print("Operação cancelada.")
        return
    
    # 2. Listar arquivos suportados
    arquivos = listar_arquivos_suportados(pasta)
    if not arquivos:
        print(f"Nenhum arquivo .xls, .xlsx ou .csv encontrado na pasta: {pasta}")
        return
    
    # 3. Permitir seleção de arquivos
    arquivos_selecionados = selecionar_arquivos(arquivos)
    if not arquivos_selecionados:
        print("Nenhum arquivo foi selecionado. Operação cancelada.")
        return
    
    print(f"\nArquivos selecionados na ordem:")
    for i, arquivo in enumerate(arquivos_selecionados, 1):
        print(f"{i}. {arquivo}")
    
    # 4. Unir arquivos
    df_resultado = unir_arquivos(pasta, arquivos_selecionados)
    if df_resultado is None:
        print("Erro ao processar os arquivos.")
        return
    
    # 5. Salvar arquivo final
    if salvar_arquivo_final(pasta, df_resultado):
        print(f"\n🎉 Processo concluído com sucesso!")
        print(f"Arquivo 'unidos.xlsx' criado na pasta: {pasta}")
    else:
        print("Erro ao salvar o arquivo final.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")