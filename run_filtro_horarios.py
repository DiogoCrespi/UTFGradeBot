#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DB_CONFIG
from typing import List, Dict, Set
from db.db import Database

# Configura a codificação para UTF-8 no Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

class FiltradorHorarios:
    """Classe para filtrar horários de aulas do banco de dados"""

    def __init__(self):
        self.db = Database()
        self.padrao_horario = re.compile(r'(\d[MTN]\d)(?:\([^)]+\))?')

    def obter_dados_curso(self) -> List[Dict]:
        """
        Obtém os dados do curso de Ciência da Computação em Medianeira do banco de dados
        """
        try:
            # Query para obter todas as disciplinas, turmas e horários do curso
            query = """
                SELECT 
                    d.codigo,
                    d.nome as disciplina,
                    t.codigo as turma,
                    t.professor,
                    h.dia_semana,
                    h.turno,
                    h.aula_inicio,
                    h.aula_fim,
                    h.sala
                FROM cursos c
                JOIN curso_disciplinas cd ON c.id = cd.curso_id
                JOIN disciplinas d ON cd.disciplina_id = d.id
                JOIN turmas t ON d.id = t.disciplina_id
                JOIN horarios h ON t.id = h.turma_id
                WHERE c.nome = '219Ciência Computação'
                AND c.campus = 'Medianeira'
                ORDER BY d.codigo, t.codigo, h.dia_semana, h.turno, h.aula_inicio;
            """
            
            resultados = self.db.execute_query(query)
            
            # Agrupa os resultados por disciplina e turma
            dados = []
            disciplina_atual = None
            turma_atual = None
            
            for row in resultados:
                # Formata o horário no formato esperado (ex: 2M1(I11))
                horario = f"{row['dia_semana']}{row['turno']}{row['aula_inicio']}({row['sala']})"
                
                if not disciplina_atual or disciplina_atual['codigo'] != row['codigo']:
                    # Nova disciplina
                    disciplina_atual = {
                        'codigo': row['codigo'],
                        'disciplina': row['disciplina'],
                        'turma': row['turma'],
                        'professor': row['professor'],
                        'horario': horario
                    }
                    dados.append(disciplina_atual)
                elif turma_atual != row['turma']:
                    # Nova turma da mesma disciplina
                    turma_atual = row['turma']
                    disciplina_atual = {
                        'codigo': row['codigo'],
                        'disciplina': row['disciplina'],
                        'turma': row['turma'],
                        'professor': row['professor'],
                        'horario': horario
                    }
                    dados.append(disciplina_atual)
                else:
                    # Mesma turma, adiciona o horário
                    disciplina_atual['horario'] += f" - {horario}"
            
            return dados
            
        except Exception as e:
            raise Exception(f"Erro ao obter dados do banco: {str(e)}")

    def filtrar_horarios(self, dados: List[Dict], horario_busca: str) -> List[Dict]:
        """
        Filtra as aulas pelo horário especificado
        """
        resultados = []

        for aula in dados:
            # Encontra todos os horários no formato dTa (d=dia, T=turno, a=aula)
            horarios = [match.group(1) for match in self.padrao_horario.finditer(aula['horario'])]

            if horario_busca in horarios:
                resultados.append(aula)

        return resultados

    def filtrar_varios_horarios(self, dados: List[Dict], horarios_busca: Set[str]) -> List[Dict]:
        """
        Filtra as aulas que tem todos seus horários dentro do conjunto informado

        Args:
            dados: Lista de dicionários com os dados das aulas
            horarios_busca: Conjunto de horários permitidos (ex: {'2M1', '2M2', '4M3'})

        Returns:
            Lista de aulas que têm todos seus horários dentro do conjunto informado
        """
        resultados = []

        for aula in dados:
            # Encontra todos os horários da aula
            horarios_aula = set(match.group(1) for match in self.padrao_horario.finditer(aula['horario']))

            # Verifica se todos os horários da aula estão no conjunto de busca
            if horarios_aula.issubset(horarios_busca):
                resultados.append(aula)

        return resultados

    def exibir_resultados(self, resultados: List[Dict]):
        """
        Exibe os resultados formatados
        """
        if not resultados:
            print("\nNenhuma aula encontrada com o(s) horário(s) especificado(s).")
            return

        print("\nAulas encontradas:")
        print("-" * 80)
        for aula in resultados:
            if aula['codigo']:
                print(f"Código: {aula['codigo']}")
                print(f"Disciplina: {aula['disciplina']}")
            print(f"Turma: {aula['turma']}")
            print(f"Horário: {aula['horario']}")
            print(f"Professor: {aula['professor']}")
            print("-" * 80)

def validar_formato_horario(horario: str) -> bool:
    """Valida se o horário está no formato correto"""
    return bool(re.match(r'^[2-6][MTN][1-6]$', horario))

def main():
    """Função principal do programa"""
    filtrador = FiltradorHorarios()

    while True:
        # Limpa a tela
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("╔════════════════════════════════════════════════════════════╗")
        print("║               FILTRADOR DE HORÁRIOS DE AULAS               ║")
        print("╠════════════════════════════════════════════════════════════╣")
        print("║                                                           ║")
        print("║  Este programa filtra horários de aulas do curso de       ║")
        print("║  Ciência da Computação em Medianeira.                     ║")
        print("║                                                           ║")
        print("║  Opções disponíveis:                                      ║")
        print("║                                                           ║")
        print("║  1. Buscar por um horário específico                      ║")
        print("║  2. Informar horários disponíveis                         ║")
        print("║  0. Sair                                                  ║")
        print("║                                                           ║")
        print("╚════════════════════════════════════════════════════════════╝")

        opcao = input("\nEscolha uma opção (0-2): ").strip()

        if opcao == "1":
            while True:
                print("\n╔════════════════════════════════════════════════════════════╗")
                print("║                  BUSCA POR HORÁRIO ESPECÍFICO              ║")
                print("╚════════════════════════════════════════════════════════════╝")
                print("\nFormato do horário: dTa (d=dia[2-6], T=turno[M,T,N], a=aula[1-6])")
                print("Exemplo: 2M1 (Segunda-feira, Manhã, primeira aula)")
                horario = input("\nDigite o horário que deseja buscar (ou 'voltar' para retornar): ").strip().upper()

                if horario.lower() == 'voltar':
                    break

                if not validar_formato_horario(horario):
                    print("\n❌ Erro: Formato de horário inválido.")
                    input("\nPressione ENTER para tentar novamente...")
                    continue

                try:
                    dados = filtrador.obter_dados_curso()
                    resultados = filtrador.filtrar_horarios(dados, horario)
                    filtrador.exibir_resultados(resultados)
                    input("\nPressione ENTER para continuar...")
                    break
                except Exception as e:
                    print(f"\n❌ Erro ao processar dados: {str(e)}")
                    input("\nPressione ENTER para tentar novamente...")

        elif opcao == "2":
            while True:
                print("\n╔════════════════════════════════════════════════════════════╗")
                print("║                BUSCA POR HORÁRIOS DISPONÍVEIS              ║")
                print("╚════════════════════════════════════════════════════════════╝")
                print("\nInforme os horários disponíveis separados por espaço")
                print("Formato: dTa (d=dia[2-6], T=turno[M,T,N], a=aula[1-6])")
                print("Exemplo: 2M1 2M2 4M3 6M1")
                print("\nDigite 'voltar' para retornar ao menu principal")

                horarios_input = input("\nDigite os horários: ").strip()
                
                if horarios_input.lower() == 'voltar':
                    break

                horarios_input = [h.upper() for h in horarios_input.split()]

                # Valida todos os horários
                if not all(validar_formato_horario(h) for h in horarios_input):
                    print("\n❌ Erro: Um ou mais horários estão em formato inválido.")
                    input("\nPressione ENTER para tentar novamente...")
                    continue

                # Converte lista para conjunto para busca mais eficiente
                horarios_busca = set(horarios_input)

                try:
                    dados = filtrador.obter_dados_curso()
                    resultados = filtrador.filtrar_varios_horarios(dados, horarios_busca)
                    filtrador.exibir_resultados(resultados)
                    input("\nPressione ENTER para continuar...")
                    break
                except Exception as e:
                    print(f"\n❌ Erro ao processar dados: {str(e)}")
                    input("\nPressione ENTER para tentar novamente...")

        elif opcao == "0":
            print("\nObrigado por usar o Filtrador de Horários!")
            break

        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER para tentar novamente...")

if __name__ == "__main__":
    main()