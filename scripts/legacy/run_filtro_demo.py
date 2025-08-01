#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
from typing import List, Dict, Set

# Configura a codificação para UTF-8 no Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

class FiltradorHorariosDemo:
    """Classe para filtrar horários de aulas com dados simulados"""

    def __init__(self):
        self.padrao_horario = re.compile(r'(\d[MTN]\d)(?:\([^)]+\))?')
        self.dados_simulados = self.criar_dados_simulados()

    def criar_dados_simulados(self) -> List[Dict]:
        """Cria dados simulados do curso de Ciência da Computação"""
        return [
            {
                'codigo': 'COM1005',
                'disciplina': 'Comunicação De Dados',
                'turma': 'CC1',
                'professor': 'Hamilton Pereira Da Silva',
                'horario': '2M1(I11) - 2M2(I11)'
            },
            {
                'codigo': 'COM1006',
                'disciplina': 'Fundamentos De Programação',
                'turma': 'CC1',
                'professor': 'Cesar Angonese',
                'horario': '2M3(I11) - 2M4(I11) - 2M5(I11) - 2M6(I11)'
            },
            {
                'codigo': 'COM1007',
                'disciplina': 'Introdução À Ciência Da Computação',
                'turma': 'CC1',
                'professor': 'Alessandra Bortoletto Garbelotti Hoffmann',
                'horario': '4M3(I11) - 4M4(I11) - 4M5(I11)'
            },
            {
                'codigo': 'COM1008',
                'disciplina': 'Lógica Matemática',
                'turma': 'CC1',
                'professor': 'Nelson Miguel Betzek',
                'horario': '3M1(I11) - 3M2(I11) - 3M3(I11) - 3M4(I11)'
            },
            {
                'codigo': 'MAT1001',
                'disciplina': 'Fundamentos De Matemática',
                'turma': 'CC1',
                'professor': 'Tatiane Tambarussi Thomaz',
                'horario': '2M3(I11) - 2M4(I11) - 2M5(I11) - 2M6(I11)'
            },
            {
                'codigo': 'MAT1002',
                'disciplina': 'Estruturas Geométricas E Vetores',
                'turma': 'CC3',
                'professor': 'Tatiane Cardoso Batista Flores',
                'horario': '3M1(I11) - 3M2(I11) - 3M3(I11)'
            },
            {
                'codigo': 'MAT1003',
                'disciplina': 'Matemática Univariável',
                'turma': 'CC2',
                'professor': 'Tatiane Cardoso Batista Flores',
                'horario': '4M1(I11) - 4M2(I11) - 4M3(I11) - 4M4(I11)'
            },
            {
                'codigo': 'MAT1004',
                'disciplina': 'Álgebra Linear',
                'turma': 'CC4',
                'professor': 'Fausto Pinheiro Da Silva',
                'horario': '5M1(I11) - 5M2(I11) - 5M3(I11)'
            },
            {
                'codigo': 'FIS1001',
                'disciplina': 'Física Do Movimento',
                'turma': 'ELE3',
                'professor': 'Sheyse Martins De Carvalho',
                'horario': '6M1(I11) - 6M2(I11) - 6M3(I11)'
            },
            {
                'codigo': 'HLA1001',
                'disciplina': 'Leitura E Escrita Acadêmica',
                'turma': 'CC5',
                'professor': 'Dayse Grassi Bernardon',
                'horario': '2M1(I11) - 2M2(I11)'
            }
        ]

    def obter_dados_curso(self) -> List[Dict]:
        """Retorna os dados simulados do curso"""
        return self.dados_simulados

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
    filtrador = FiltradorHorariosDemo()

    while True:
        # Limpa a tela
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("╔════════════════════════════════════════════════════════════╗")
        print("║               FILTRADOR DE HORÁRIOS DE AULAS               ║")
        print("╠════════════════════════════════════════════════════════════╣")
        print("║                                                           ║")
        print("║  Este programa filtra horários de aulas do curso de       ║")
        print("║  Ciência da Computação em Medianeira (DEMO).              ║")
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
                print("Horários disponíveis: 2M1, 2M2, 2M3, 2M4, 2M5, 2M6, 3M1, 3M2, 3M3, 3M4, 4M1, 4M2, 4M3, 4M4, 4M5, 5M1, 5M2, 5M3, 6M1, 6M2, 6M3")
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