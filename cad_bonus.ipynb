{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "73d6c517",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Bibliotecas\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import psycopg2 "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "66433196",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Conexão estabelecida com sucesso!\n"
     ]
    }
   ],
   "source": [
    "# Configurações de conexão\n",
    "config = {\n",
    "    'host': '10.100.1.86',        # ou o endereço do seu servidor\n",
    "    'database': 'bd_bonus',\n",
    "    'user': 'giovanni_aud',\n",
    "    'password': 'Bonus@2025',\n",
    "    'port': 5432               # porta padrão do PostgreSQL\n",
    "}\n",
    "# Conectar ao banco de dados\n",
    "conn = psycopg2.connect(**config)\n",
    "cursor = conn.cursor()\n",
    "\n",
    "\n",
    "print(\"Conexão estabelecida com sucesso!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "a170ca10",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "Index(['idnfsexterno', 'data_emissao_proposta', 'data_ajustada', 'valor_bonus',\n",
       "       'rebate', 'reembolso_ipva', 'comissao_vd', 'trade', 'portal', 'varejo',\n",
       "       'equalizacao', 'trade_in', 'taxa_0', 'ipva', 'wallbox', 'portatil',\n",
       "       'seguro', 'refaturado', 'em_valid', 'opt_comecial', 'campanha',\n",
       "       'detalhes'],\n",
       "      dtype='object')"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "sheets = pd.read_csv('sheets.csv')\n",
    "sheets.columns"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "47da2f87",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "byd\n",
      "dep_union\n",
      "information_schema\n",
      "pg_catalog\n",
      "pg_toast\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"SELECT schema_name FROM information_schema.schemata;\")\n",
    "schemas = cursor.fetchall()\n",
    "for schema in schemas:\n",
    "    print(schema[0])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "03ebdf04",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "union_view_bq\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'dep_union';\")\n",
    "tables = cursor.fetchall()\n",
    "for table in tables:\n",
    "    print(table[0])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "57ff00b7",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "bonus_view\n",
      "byd_cadastro\n",
      "db_vendas_byd\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'byd';\")\n",
    "tables_byd = cursor.fetchall()\n",
    "for table in tables_byd:\n",
    "    print(table[0])\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "8c6f151b",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Todas as linhas da tabela db_vendas_byd foram apagadas com sucesso!\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"DELETE FROM byd.db_vendas_byd;\")\n",
    "conn.commit()\n",
    "print(\"Todas as linhas da tabela db_vendas_byd foram apagadas com sucesso!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "3a21b6a1",
   "metadata": {},
   "source": [
    "##### Desativar FK "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "bfa6a275",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Constraint fk_idnfsexterno removida da tabela byd.byd_cadastro\n",
      "Todas as foreign keys foram desativadas (removidas) do banco de dados.\n"
     ]
    }
   ],
   "source": [
    "# Desativar todas as foreign keys do banco de dados\n",
    "# Busca todas as constraints do tipo FOREIGN KEY\n",
    "cursor.execute(\"\"\"\n",
    "SELECT tc.table_schema, tc.table_name, tc.constraint_name \n",
    "FROM information_schema.table_constraints AS tc \n",
    "WHERE tc.constraint_type = 'FOREIGN KEY'\n",
    "\"\"\")\n",
    "fks = cursor.fetchall()\n",
    "\n",
    "# Desativa cada constraint encontrada\n",
    "for schema, table, constraint in fks:\n",
    "    sql = f'ALTER TABLE \"{schema}\".\"{table}\" DROP CONSTRAINT \"{constraint}\";'\n",
    "    try:\n",
    "        cursor.execute(sql)\n",
    "        print(f'Constraint {constraint} removida da tabela {schema}.{table}')\n",
    "    except Exception as e:\n",
    "        print(f'Erro ao remover constraint {constraint} da tabela {schema}.{table}: {e}')\n",
    "        conn.rollback()  # Limpa o erro da transação para continuar\n",
    "\n",
    "conn.commit()\n",
    "print('Todas as foreign keys foram desativadas (removidas) do banco de dados.')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "15561bcb",
   "metadata": {},
   "outputs": [],
   "source": [
    "conn.rollback()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "4be92dc7",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Foreign key fk_idnfsexterno foi reativada na tabela byd.byd_cadastro\n"
     ]
    }
   ],
   "source": [
    "# Reativar a foreign key que foi removida\n",
    "cursor.execute(\"\"\"\n",
    "ALTER TABLE \"byd\".\"byd_cadastro\" \n",
    "ADD CONSTRAINT \"fk_idnfsexterno\" \n",
    "FOREIGN KEY (idnfsexterno) \n",
    "REFERENCES byd.db_vendas_byd(idnfsexterno);\n",
    "\"\"\")\n",
    "conn.commit()\n",
    "print('Foreign key fk_idnfsexterno foi reativada na tabela byd.byd_cadastro')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "1b75a4e9",
   "metadata": {},
   "source": [
    "##### Migrar Data Cadastro_Bonus"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "d195e520",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "idnfsexterno: text\n",
      "data_emissao_proposta: date\n",
      "data_ajustada: date\n",
      "valor_bonus: numeric\n",
      "rebate: text\n",
      "reembolso_ipva: text\n",
      "comissao_vd: text\n",
      "trade: text\n",
      "portal: text\n",
      "varejo: text\n",
      "equalizacao: boolean\n",
      "trade_in: boolean\n",
      "taxa_0: boolean\n",
      "ipva: boolean\n",
      "wallbox: boolean\n",
      "portatil: boolean\n",
      "seguro: boolean\n",
      "refaturado: boolean\n",
      "em_valid: text\n",
      "opt_comecial: text\n",
      "campanha: text\n",
      "detalhes: text\n",
      "tipo_transacao: character varying\n",
      "status_nf: character varying\n",
      "bonus_utilizado: text\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'byd' AND table_name = 'byd_cadastro';\")\n",
    "columns = cursor.fetchall()\n",
    "for column in columns:\n",
    "    print(f\"{column[0]}: {column[1]}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "dd8aed54",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Coluna data_ajustada alterada para tipo timestamp com sucesso!\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"\"\"\n",
    "ALTER TABLE \"byd\".\"byd_cadastro\" \n",
    "ALTER COLUMN data_ajustada TYPE timestamp;\n",
    "\"\"\")\n",
    "conn.commit()\n",
    "print('Coluna data_ajustada alterada para tipo timestamp com sucesso!')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "1c8e0f5c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "View byd.bonus_view foi removida com sucesso!\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"DROP VIEW byd.bonus_view;\")\n",
    "conn.commit()\n",
    "conn.rollback()\n",
    "print('View byd.bonus_view foi removida com sucesso!')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "a6d83d7e",
   "metadata": {},
   "outputs": [],
   "source": [
    "conn.rollback()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e0cb42fe",
   "metadata": {},
   "outputs": [
    {
     "ename": "DatatypeMismatch",
     "evalue": "column \"dta_processamento\" cannot be cast automatically to type timestamp without time zone\nHINT:  You might need to specify \"USING dta_processamento::timestamp without time zone\".\n",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mDatatypeMismatch\u001b[0m                          Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[25], line 1\u001b[0m\n\u001b[1;32m----> 1\u001b[0m cursor\u001b[38;5;241m.\u001b[39mexecute(\u001b[38;5;124m\"\"\"\u001b[39m\n\u001b[0;32m      2\u001b[0m \u001b[38;5;124mALTER TABLE \u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mbyd\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124m.\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mdb_vendas_byd\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124m \u001b[39m\n\u001b[0;32m      3\u001b[0m \u001b[38;5;124mALTER COLUMN dta_processamento TYPE timestamp;\u001b[39m\n\u001b[0;32m      4\u001b[0m \u001b[38;5;124m\"\"\"\u001b[39m)\n\u001b[0;32m      5\u001b[0m conn\u001b[38;5;241m.\u001b[39mcommit()\n\u001b[0;32m      6\u001b[0m \u001b[38;5;28mprint\u001b[39m(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mColuna dta_processamento alterada para tipo timestamp com sucesso!\u001b[39m\u001b[38;5;124m'\u001b[39m)\n",
      "\u001b[1;31mDatatypeMismatch\u001b[0m: column \"dta_processamento\" cannot be cast automatically to type timestamp without time zone\nHINT:  You might need to specify \"USING dta_processamento::timestamp without time zone\".\n"
     ]
    }
   ],
   "source": [
    "# 1. Descobrir views que usam a coluna dta_processamento\n",
    "cursor.execute(\"\"\"\n",
    "SELECT table_schema, table_name, view_definition \n",
    "FROM information_schema.views \n",
    "WHERE view_definition ILIKE '%dta_processamento%'\n",
    "  AND table_schema = 'byd';\n",
    "\"\"\")\n",
    "views = cursor.fetchall()\n",
    "for schema, view, definition in views:\n",
    "    print(f\"View encontrada: {schema}.{view}\")\n",
    "\n",
    "# 2. Remover as views encontradas (exemplo para uma view chamada bonus_view)\n",
    "try:\n",
    "    cursor.execute(\"DROP VIEW IF EXISTS byd.bonus_view;\")\n",
    "    conn.commit()\n",
    "    print('View byd.bonus_view removida!')\n",
    "except Exception as e:\n",
    "    print(f'Erro ao remover a view: {e}')\n",
    "    conn.rollback()\n",
    "\n",
    "# 3. Alterar o tipo da coluna\n",
    "try:\n",
    "    cursor.execute(\"\"\"\n",
    "    ALTER TABLE \"byd\".\"db_vendas_byd\" \n",
    "    ALTER COLUMN dta_processamento TYPE timestamp;\n",
    "    \"\"\")\n",
    "    conn.commit()\n",
    "    print('Coluna dta_processamento alterada para tipo timestamp com sucesso!')\n",
    "except Exception as e:\n",
    "    print(f'Erro ao alterar a coluna: {e}')\n",
    "    conn.rollback()\n",
    "\n",
    "# 4. (Opcional) Recriar a view removida aqui, se necessário"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "3a1c426f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "sistema: text\n",
      "idnfsexterno: text\n",
      "data_atual: text\n",
      "data_atual_inv: text\n",
      "val_modalidade: text\n",
      "sinal: text\n",
      "revenda: text\n",
      "empresa: text\n",
      "lucbru: text\n",
      "chv_empresa: text\n",
      "bandeira_bi: text\n",
      "ordem_bandeira: text\n",
      "nome_empresa: text\n",
      "numero_nota_fiscal: text\n",
      "serie_nota_fiscal: text\n",
      "dta_entrada_saida: text\n",
      "status_nf: text\n",
      "dta_processamento: text\n",
      "dta_cancelamento: text\n",
      "tipo_transacao: text\n",
      "des_tipo_transacao: text\n",
      "tipo: text\n",
      "subtipo_transacao: text\n",
      "contador: text\n",
      "cod_cliente: text\n",
      "nome_cliente: text\n",
      "cpf: text\n",
      "cnpj: text\n",
      "fisico_juridico: text\n",
      "bairro_entrega: text\n",
      "municipio_entrega: text\n",
      "uf_entrega: text\n",
      "cod_mun: text\n",
      "vendedor: text\n",
      "nome_vendedor: text\n",
      "proposta: text\n",
      "situacao: text\n",
      "veiculo: text\n",
      "nome_departamento_veiculo: text\n",
      "novo_usado: text\n",
      "chassi: text\n",
      "placa: text\n",
      "ano_fabricacao: text\n",
      "ano_modelo: text\n",
      "modelo: text\n",
      "des_modelo: text\n",
      "marca: text\n",
      "codfamilia: text\n",
      "familia: text\n",
      "bonus: text\n",
      "val_icms: text\n",
      "val_ipi: text\n",
      "imposto_importacao: text\n",
      "val_pis: text\n",
      "val_cofins: text\n",
      "nota_origem_devolucao: text\n",
      "dta_nota_origem_devolucao: text\n",
      "transacao_origem_devolucao: text\n",
      "dta_compra: text\n",
      "valor_venda: text\n",
      "valor_desconto: text\n",
      "valor_venda_bruta: text\n",
      "val_custo_contabil: text\n",
      "val_cortesias: text\n",
      "usado: text\n",
      "novo: text\n",
      "venda_direta: text\n",
      "cep_entrega: text\n",
      "latitude: text\n",
      "longitude: text\n",
      "tipo_venda: text\n",
      "bairro_formatado: text\n",
      "uf_formatada: text\n",
      "municipio_formatado: text\n",
      "ano_mes: text\n",
      "id: text\n",
      "ano_modelo_formatado: text\n",
      "devolucao_flag: text\n"
     ]
    }
   ],
   "source": [
    "cursor.execute(\"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'byd' AND table_name = 'db_vendas_byd';\")\n",
    "columns = cursor.fetchall()\n",
    "for column in columns:\n",
    "    print(f\"{column[0]}: {column[1]}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "55542ef4",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "base",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
