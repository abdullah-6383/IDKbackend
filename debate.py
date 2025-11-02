import json
import google.generativeai as genai
from typing import Dict, List


class DebateAgent:
    def __init__(self, name: str, role: str, knowledge_files: List[str], api_key: str):
        self.name = name
        self.role = role
        self.knowledge = self._load_knowledge(knowledge_files)
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    def _load_knowledge(self, knowledge_files: List[str]) -> str:
        combined_knowledge = []
        
        for file_path in knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    file_info = f"\n=== Knowledge from {data['source_file']} ===\n"
                    file_info += f"Topic: {data['topic']}\n\n"
                    
                    for item in data['items']:
                        file_info += f"Statement: {item['text']}\n"
                        file_info += f"Bias: {item['bias_x']}, Significance: {item['significance_y']}\n"
                        
                        if item['relevant_links']:
                            file_info += "Supporting Evidence:\n"
                            for link in item['relevant_links']:
                                file_info += f"  - {link['title']}\n"
                                file_info += f"    URL: {link['link']}\n"
                                file_info += f"    Trust Score: {link['trust_score']} ({link['source_type']})\n"
                                file_info += f"    Snippet: {link['snippet']}\n"
                                if 'extracted_content' in link:
                                    content_preview = link['extracted_content'][:300]
                                    file_info += f"    Content: {content_preview}...\n"
                                file_info += "\n"
                        file_info += "\n"
                    
                    combined_knowledge.append(file_info)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return "\n".join(combined_knowledge)
    
    def make_argument(self, topic: str, debate_context: str = "") -> str:
        prompt = f"""You are {self.name}, representing a {self.role} perspective in a debate.

TOPIC TO DEBATE: {topic}

YOUR KNOWLEDGE BASE:
{self.knowledge}

{debate_context}

Based on your knowledge base, make a clear, evidence-based argument about whether the topic/information is trustworthy.

Rules:
1. Focus ONLY on the topic at hand - not all topics are political
2. Use concrete evidence from your knowledge base (cite sources and trust scores)
3. Your perspective comes from the sources you have access to ({self.role} sources), not from political ideology
4. Be concise and clear - aim for 150-200 words
5. Focus on: source credibility, evidence quality, factual accuracy
6. Explain your reasoning simply and logically

Your argument:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.6, 'max_output_tokens': 400}
            )
            return response.text.strip()
        except Exception as e:
            return f"Error generating argument: {str(e)}"
    
    def respond_to_opponent(self, topic: str, opponent_argument: str, debate_history: str) -> str:
        prompt = f"""You are {self.name}, representing a {self.role} perspective in a debate.

TOPIC: {topic}

YOUR KNOWLEDGE BASE:
{self.knowledge}

DEBATE HISTORY:
{debate_history}

OPPONENT'S LATEST ARGUMENT:
{opponent_argument}

Respond to your opponent's argument about the TOPIC. Counter their points with your evidence.

Rules:
1. Stay focused on the topic - "{topic}"
2. Directly address opponent's specific claims with evidence from your knowledge base
3. Point out if their sources are less trustworthy than yours (compare trust scores)
4. Be concise and clear - aim for 150-200 words
5. Use simple language that's easy to understand
6. Don't make it political unless the topic itself is political

Your response:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.6, 'max_output_tokens': 400}
            )
            return response.text.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"


class JudgeAgent:
    def __init__(self, api_key: str):
        self.name = "Judge"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    def evaluate_debate(self, topic: str, debate_transcript: str) -> Dict[str, any]:
        prompt = f"""You are an impartial JUDGE evaluating a debate about the trustworthiness of information.

TOPIC: {topic}

FULL DEBATE TRANSCRIPT:
{debate_transcript}

Your task is to provide a final TRUST SCORE from 0-100% based on the debate.

Trust Score Scale:
- 0-20%: Highly untrustworthy - Poor sources, weak evidence, contradictory information
- 21-40%: Mostly untrustworthy - Significant concerns about credibility
- 41-60%: Mixed reliability - Some valid points but major concerns remain
- 61-80%: Mostly trustworthy - Good sources and evidence with minor concerns
- 81-100%: Highly trustworthy - Excellent sources, strong evidence, consistent information

Evaluation Criteria:
- Quality and trustworthiness of sources cited (trust scores)
- Strength of evidence presented by both sides
- Logical consistency of arguments
- Which side had more credible sources and stronger evidence
- Overall credibility of the claims about this specific topic

Provide your judgment in the following format:

TRUST SCORE: [0-100]%

REASONING:
[In 150-200 words, explain your trust score clearly and simply. Analyze both sides' arguments and evidence. Use plain language that anyone can understand.]

KEY FACTORS:
- [List 3-4 key factors that influenced your trust score]

Your judgment:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.4, 'max_output_tokens': 600}
            )
            
            text = response.text.strip()
            
            trust_score = 50  # Default to middle if parsing fails
            if "TRUST SCORE:" in text:
                score_line = text.split("TRUST SCORE:")[1].split("\n")[0].strip()
                # Extract number from string like "75%" or "75"
                import re
                numbers = re.findall(r'\d+', score_line)
                if numbers:
                    trust_score = int(numbers[0])
                    # Ensure it's within 0-100
                    trust_score = max(0, min(100, trust_score))
            
            return {
                'trust_score': trust_score,
                'full_judgment': text
            }
        except Exception as e:
            return {
                'trust_score': 0,
                'full_judgment': f"Error generating judgment: {str(e)}"
            }


class DebateOrchestrator:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config['api_key']
        
        with open('data/input.json', 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        self.topic = input_data['topic']
        
        self.leftist = DebateAgent(
            name="Leftist Agent",
            role="analyst with access to leftist-leaning sources",
            knowledge_files=['relevant_common.json', 'relevant_leftist.json'],
            api_key=api_key
        )
        
        self.rightist = DebateAgent(
            name="Rightist Agent",
            role="analyst with access to rightist-leaning sources",
            knowledge_files=['relevant_common.json', 'relevant_rightist.json'],
            api_key=api_key
        )
        
        self.judge = JudgeAgent(api_key=api_key)
        
        self.debate_transcript = []
    
    def check_if_debate_ready_for_conclusion(self, debate_history: str) -> Dict[str, any]:
        """Check if the debate has reached sufficient depth for a conclusion."""
        prompt = f"""You are monitoring a debate about information trustworthiness.

TOPIC: {self.topic}

DEBATE SO FAR:
{debate_history}

Assess if the debate is ready for a final conclusion. The debate is ready if:
1. Both sides have presented their main evidence and arguments
2. Key counterarguments have been addressed
3. The evidence has been sufficiently examined
4. Further debate would likely be repetitive

Respond in this format:

READY: [YES / NO]

REASON: [Brief 1-2 sentence explanation]

If NO, also provide:
NEED: [What still needs to be addressed in 1 sentence]

Your assessment:"""

        try:
            response = self.judge.model.generate_content(
                prompt,
                generation_config={'temperature': 0.3, 'max_output_tokens': 200}
            )
            
            text = response.text.strip()
            
            is_ready = False
            if "READY:" in text:
                ready_line = text.split("READY:")[1].split("\n")[0].strip()
                is_ready = "YES" in ready_line.upper()
            
            return {
                'ready': is_ready,
                'full_response': text
            }
        except Exception as e:
            print(f"Error checking debate readiness: {e}")
            return {'ready': False, 'full_response': f"Error: {e}"}
    
    def conduct_debate(self, max_rounds: int = 5, min_rounds: int = 1):
        print("="*70)
        print("DEBATE: INFORMATION TRUSTWORTHINESS ANALYSIS")
        print("="*70)
        print(f"\nTOPIC: {self.topic}\n")
        print("="*70)
        
        print("\n[LEFTIST AGENT - Opening Statement]\n")
        leftist_opening = self.leftist.make_argument(self.topic)
        print(leftist_opening)
        self.debate_transcript.append(f"LEFTIST OPENING:\n{leftist_opening}\n")
        
        print("\n" + "="*70)
        print("\n[RIGHTIST AGENT - Opening Statement]\n")
        rightist_opening = self.rightist.make_argument(self.topic)
        print(rightist_opening)
        self.debate_transcript.append(f"RIGHTIST OPENING:\n{rightist_opening}\n")
        
        debate_history = "\n\n".join(self.debate_transcript)
        
        round_num = 0
        rightist_response = rightist_opening
        
        while round_num < max_rounds:
            round_num += 1
            
            print("\n" + "="*70)
            print(f"\n[ROUND {round_num} - LEFTIST REBUTTAL]\n")
            
            leftist_response = self.leftist.respond_to_opponent(
                self.topic,
                rightist_response,
                debate_history
            )
            print(leftist_response)
            self.debate_transcript.append(f"LEFTIST ROUND {round_num}:\n{leftist_response}\n")
            debate_history = "\n\n".join(self.debate_transcript)
            
            print("\n" + "="*70)
            print(f"\n[ROUND {round_num} - RIGHTIST REBUTTAL]\n")
            
            rightist_response = self.rightist.respond_to_opponent(
                self.topic,
                leftist_response,
                debate_history
            )
            print(rightist_response)
            self.debate_transcript.append(f"RIGHTIST ROUND {round_num}:\n{rightist_response}\n")
            debate_history = "\n\n".join(self.debate_transcript)
            
            # Check if debate is ready for conclusion (after minimum rounds)
            if round_num >= min_rounds:
                print("\n" + "="*70)
                print("\n[Checking if debate is ready for conclusion...]\n")
                
                readiness = self.check_if_debate_ready_for_conclusion(debate_history)
                print(readiness['full_response'])
                
                if readiness['ready']:
                    print("\n✓ Debate has reached sufficient depth. Proceeding to verdict.\n")
                    break
                else:
                    print("\n→ Debate continues...\n")
        
        if round_num >= max_rounds:
            print(f"\n⚠ Maximum rounds ({max_rounds}) reached. Proceeding to verdict.\n")
        
        print("\n" + "="*70)
        print("\n[JUDGE - FINAL VERDICT]\n")
        
        full_transcript = "\n\n".join(self.debate_transcript)
        judgment = self.judge.evaluate_debate(self.topic, full_transcript)
        
        print(judgment['full_judgment'])
        
        print("\n" + "="*70)
        
        result = {
            'topic': self.topic,
            'debate_transcript': self.debate_transcript,
            'trust_score': judgment['trust_score'],
            'judgment': judgment['full_judgment']
        }
        
        with open('debate_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Debate result saved to debate_result.json")
        print(f"✓ Final Trust Score: {judgment['trust_score']}%")
        
        return result


def main():
    orchestrator = DebateOrchestrator()
    # Debate will continue until proper conclusion (max 5 rounds, min 1 round before checking)
    orchestrator.conduct_debate(max_rounds=5, min_rounds=1)


if __name__ == "__main__":
    main()
