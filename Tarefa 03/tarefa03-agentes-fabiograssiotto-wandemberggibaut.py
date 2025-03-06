from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import math
import getpass

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # TODO
    # Esta função recebe o nome de um restaurante e retorna as avaliações desse restaurante.
    # A saída deve ser um dicionário, onde a chave é o nome do restaurante e o valor é uma lista de avaliações desse restaurante.
    # O "agente de busca de dados" deve ter acesso à assinatura desta função e deve ser capaz de sugeri-la como uma chamada de função.
    # Exemplo:
    # > fetch_restaurant_data("Estação Barão")
    # {"Estação Barão's": ["A comida do Estação Barão foi mediana, sem nada particularmente marcante.", ...]}

    # Dicionátio que armazena o nome do restaurante e suas avaliações
    restaurant_reviews = {}
    current_restaurant = None

    # Abre o arquivo restaurantes.txt e cria estrutura para armazenar os dados
    with open('restaurantes.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # Divide a linha pelo primeiro ponto encontrado
            parts = line.split('.', 1)
            if len(parts) == 2:
                current_restaurant, review = parts
                current_restaurant = current_restaurant.strip()
                review = review.strip()
                if current_restaurant not in restaurant_reviews:
                    restaurant_reviews[current_restaurant] = []
                restaurant_reviews[current_restaurant].append(review)

    # Retorna a review do restaurante
    return {restaurant_name: restaurant_reviews.get(restaurant_name, [])}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # Esta função recebe o nome de um restaurante, uma lista de notas da comida (de 1 a 5) e uma lista de notas do atendimento ao cliente (de 1 a 5).
    # A saída deve ser uma pontuação entre 0 e 10, calculada da seguinte forma:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # A fórmula acima é uma média geométrica das notas, que penaliza mais a qualidade da comida do que o atendimento ao cliente.
    # Exemplo:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # OBSERVAÇÃO: Certifique-se de que a pontuação inclui PELO MENOS 3 casas decimais. Os testes públicos só aceitarão pontuações 
    # que tenham no mínimo 3 casas decimais.

    # Sanity check das notas passadas como parâmetro
    if len(food_scores) != len(customer_service_scores):
        raise ValueError("As listas de notas de comida e atendimento ao cliente devem ter o mesmo comprimento.")

    # Número de avaliações
    N = len(food_scores)

    # Calcula a pontuação geral usando a fórmula fornecida
    overall_score = sum(math.sqrt(food_scores[i]**2 * customer_service_scores[i]) for i in range(N)) * (1 / (N * math.sqrt(125))) * 10

    # Retorna a pontuação com pelo menos 3 casas decimais
    return {restaurant_name: round(overall_score, 3)}

def setup_llm():
    api_key = os.environ.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") or getpass.getpass("Enter your Groq API key: ")

    config_list = [
        {
            'model': 'llama-3.3-70b-versatile',
            'api_key': api_key,
            "api_type": "groq"
        },
    ]
    llm_config = {"config_list": config_list}
    return llm_config
    

# Não modifique a assinatura da função "main".
def main(user_query: str):
    entrypoint_agent_system_message = "" # TODO
    # Exemplo de configuração de LLM para o agente de entrada
    #llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # Groq setup
    llm_config = setup_llm()

    # O agente principal de entrada/supervisor
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Obtém as avaliações de um restaurante específico.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    # Crie mais agentes aqui.

    # TODO
    # Preencha o argumento de `initiate_chats` abaixo, chamando os agentes corretos sequencialmente.
    # Se você decidir usar outro padrão de conversação, sinta-se à vontade para ignorar este código.

    # Descomente assim que iniciar o chat com pelo menos um agente.
    # result = entrypoint_agent.initiate_chats([{}])
    
# NÃO modifique o código abaixo.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])