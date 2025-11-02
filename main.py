import json
import os
import time
from datetime import datetime
from googleapiclient.discovery import build
from typing import List, Dict, Any
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RelevanceSearchSystem:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.search_engine_id = self.config['search_engine_id']
        self.links_per_text = self.config['links_per_text']
        self.delay = self.config['rate_limiting']['delay_between_requests']
        self.max_retries = self.config['rate_limiting']['max_retries']
        
        self.search_service = build("customsearch", "v1", developerKey=self.api_key)
        
        genai.configure(api_key=self.api_key)
        self.gemini_model = genai.GenerativeModel(
            model_name=self.config['gemini_settings']['model']
        )
        
        input_file = os.path.join('data', 'input.json')
        with open(input_file, 'r', encoding='utf-8') as f:
            self.input_data = json.load(f)
        
        self.topic = self.input_data.get('topic', '')
        self.context_text = self.input_data.get('text', '')
        self.relevance_threshold = self.config['gemini_settings']['relevance_threshold']
        self.requests_per_minute = self.config['gemini_settings'].get('requests_per_minute', 10)
        self.wait_on_rate_limit = self.config['gemini_settings'].get('wait_on_rate_limit', True)
        self.request_count = 0
        self.minute_start = time.time()
        
        self.topic_keywords = self._extract_keywords_from_topic()
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--log-level=3')
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Selenium WebDriver initialized successfully\n")
        except Exception as e:
            print(f"Warning: Could not initialize Selenium WebDriver: {str(e)}")
            print("Content extraction will be skipped\n")
            self.driver = None
        
        if self.config['output_settings']['save_results']:
            os.makedirs(self.config['output_settings']['output_folder'], exist_ok=True)
    
    def _extract_keywords_from_topic(self) -> str:
        words = self.topic.split()
        important_words = []
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'by', 'with', 'from', 'is', 'was', 'are', 'were', 'calls', 'story', 'news'}
        
        for word in words:
            cleaned = word.strip('.,!?:;"()[]{}').lower()
            if len(cleaned) > 2 and cleaned not in stop_words and not cleaned.isdigit():
                important_words.append(cleaned)
        
        keywords = ' '.join(important_words[:5])
        print(f"Extracted keywords from topic: {keywords}\n")
        return keywords
    
    def rephrase_with_topic_context(self, original_text: str) -> str:
        self._manage_rate_limit()
        
        prompt = f"""You are rephrasing search queries to be more specific and contextual.

INPUT TOPIC: {self.topic}

ORIGINAL SEARCH TEXT: {original_text}

Task: Rephrase the original search text to relate it to the input topic, while preserving the original meaning and sentiment.

Rules:
1. Keep the core meaning and perspective of the original text unchanged
2. Connect it naturally to the input topic
3. Make it more specific for better search results
4. Keep it concise (under 100 words)
5. Do not add bias or change the political stance

Respond ONLY with the rephrased text, nothing else."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 150
                    }
                )
                
                self.request_count += 1
                rephrased = response.text.strip()
                return rephrased
            
            except Exception as e:
                error_str = str(e)
                # if '429' in error_str or 'quota' in error_str.lower():
                #     wait_time = 70
                #     print(f"    Rate limit hit during rephrasing, waiting {wait_time} seconds...")
                #     time.sleep(wait_time)
                #     self.request_count = 0
                #     self.minute_start = time.time()
                #     if attempt < max_retries - 1:
                #         continue
                
                print(f"    Error rephrasing: {error_str[:100]}")
                return original_text
        
        return original_text
    
    def extract_content_from_url(self, url: str) -> str:
        if not self.driver:
            return "Selenium not available - content extraction skipped"
        
        try:
            self.driver.set_page_load_timeout(15)
            self.driver.get(url)
            
            time.sleep(2)
            
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                content = body.text
            except:
                content = self.driver.page_source
            
            content = ' '.join(content.split())
            
            if len(content) > 5000:
                content = content[:5000]
            
            return content if content else "Content could not be extracted"
        
        except Exception as e:
            return f"Error extracting content: {str(e)[:100]}"
    
    def search_google(self, query: str, rephrased_query: str) -> List[Dict[str, str]]:
        search_query = f"{rephrased_query} {self.topic_keywords}"
        
        for attempt in range(self.max_retries):
            try:
                result = self.search_service.cse().list(
                    q=search_query,
                    cx=self.search_engine_id,
                    num=min(self.links_per_text, 10),
                    safe=self.config['search_settings']['safe'],
                    lr=f"lang_{self.config['search_settings']['language']}",
                    cr=f"country{self.config['search_settings']['country'].upper()}"
                ).execute()
                
                links = []
                if 'items' in result:
                    for item in result['items']:
                        links.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        })
                
                return links
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * (attempt + 1))
                    continue
                else:
                    print(f"Error searching for '{query[:50]}...': {str(e)}")
                    return []
    
    def _manage_rate_limit(self):
        # RATE LIMITING DISABLED - Uncomment code below to enable
        pass
        # current_time = time.time()
        # elapsed = current_time - self.minute_start
        
        # if elapsed >= 60:
        #     self.request_count = 0
        #     self.minute_start = current_time
        
        # if self.request_count >= self.requests_per_minute - 1:
        #     wait_time = 60 - elapsed + 3
        #     if self.wait_on_rate_limit and wait_time > 0:
        #         print(f"    Rate limit approaching, waiting {wait_time:.0f} seconds...")
        #         time.sleep(wait_time)
        #         self.request_count = 0
        #         self.minute_start = time.time()
    
    def check_trust_score(self, link_data: dict) -> dict:
        self._manage_rate_limit()
        
        url = link_data.get('link', '')
        domain = url.split('/')[2] if len(url.split('/')) > 2 else url
        
        prompt = f"""Analyze the trustworthiness and reputation of this source.

URL: {url}
Domain: {domain}
Title: {link_data.get('title', '')}
Snippet: {link_data.get('snippet', '')}

Evaluate based on:
1. Source Type: News organization, academic, government, social media, blog, etc.
2. Reputation: Known credible source vs unknown/questionable
3. Bias/Agenda: Neutral reporting vs heavily biased
4. Verification: Likely factual vs opinion/unverified claims
5. Professional Standards: Editorial oversight vs unmoderated content

Trust Score Scale:
0.9-1.0: Highly trusted (major news, academic journals, government sites)
0.7-0.89: Trusted (established media, reputable organizations)
0.5-0.69: Moderately trusted (known sources with some bias/mixed quality)
0.3-0.49: Low trust (social media posts, blogs, user-generated content)
0.0-0.29: Very low trust (unreliable sources, known misinformation)

Consider:
- Facebook/social media posts: 0.2-0.4 (user content, unverified)
- Major news outlets (NYT, WSJ, BBC, The Nation, etc.): 0.8-0.95
- Academic/research sites (.edu, .gov): 0.85-1.0
- Established organizations: 0.7-0.85
- Personal blogs/unknown sites: 0.1-0.3

Respond ONLY with a JSON object:
{{
    "trust_score": 0.0 to 1.0,
    "source_type": "type of source",
    "trust_reasoning": "brief explanation of trust score"
}}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': self.config['gemini_settings']['temperature'],
                        'max_output_tokens': 250
                    }
                )
                
                self.request_count += 1
                
                response_text = response.text.strip()
                
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text.strip())
                
                return {
                    'trust_score': result.get('trust_score', 0.5),
                    'source_type': result.get('source_type', 'Unknown'),
                    'trust_reasoning': result.get('trust_reasoning', '')
                }
            
            except Exception as e:
                error_str = str(e)
                # if '429' in error_str or 'quota' in error_str.lower():
                #     wait_time = 70
                #     print(f"    Rate limit hit, waiting {wait_time} seconds before retry...")
                #     time.sleep(wait_time)
                #     self.request_count = 0
                #     self.minute_start = time.time()
                #     if attempt < max_retries - 1:
                #         continue
                
                print(f"    Trust check error: {domain[:30]}... - {error_str[:100]}")
                return {
                    'trust_score': 0.5,
                    'source_type': 'Unknown',
                    'trust_reasoning': 'Error analyzing trust'
                }
        
        return {
            'trust_score': 0.5,
            'source_type': 'Unknown',
            'trust_reasoning': 'Max retries exceeded'
        }
    
    def check_relevance(self, link_data: dict, original_text: str) -> dict:
        self._manage_rate_limit()
        
        prompt = f"""You are analyzing web search results for relevance to a specific topic and context.

TOPIC: {self.topic}

CONTEXT: {self.context_text}

SEARCH QUERY: {original_text}

LINK TO EVALUATE:
Title: {link_data.get('title', '')}
URL: {link_data.get('link', '')}
Snippet: {link_data.get('snippet', '')}

Task: Determine if this link contains content relevant to the given topic and context.

Evaluate based on:
1. Direct mentions or references to the topic
2. Discussion of events, people, or issues mentioned in the context
3. Related news, analysis, or commentary on the topic
4. Credible sources discussing the same subject matter

NOT relevant:
- Generic articles about completely unrelated topics
- Articles about different subjects or people
- Unrelated news or content

Respond ONLY with a JSON object in this exact format:
{{
    "relevant": true or false,
    "confidence": 0.0 to 1.0,
    "reason": "brief explanation"
}}"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': self.config['gemini_settings']['temperature'],
                        'max_output_tokens': 200
                    }
                )
                
                self.request_count += 1
                
                response_text = response.text.strip()
                
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text.strip())
                
                return {
                    'relevant': result.get('relevant', False),
                    'confidence': result.get('confidence', 0.0),
                    'reason': result.get('reason', ''),
                    'link_data': link_data
                }
            
            except Exception as e:
                error_str = str(e)
                # if '429' in error_str or 'quota' in error_str.lower():
                #     wait_time = 70
                #     print(f"    Rate limit hit, waiting {wait_time} seconds before retry...")
                #     time.sleep(wait_time)
                #     self.request_count = 0
                #     self.minute_start = time.time()
                #     if attempt < max_retries - 1:
                #         continue
                
                print(f"    Relevance check error: {link_data.get('link', '')[:50]}... - {error_str[:100]}")
                return {
                    'relevant': False,
                    'confidence': 0.0,
                    'reason': f'Error: {error_str[:100]}',
                    'link_data': link_data
                }
        
        return {
            'relevant': False,
            'confidence': 0.0,
            'reason': 'Max retries exceeded',
            'link_data': link_data
        }
    
    def process_json_file(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        
        for idx, item in enumerate(data):
            text = item.get('text', '')
            if not text:
                continue
            
            print(f"Processing item {idx + 1}/{len(data)} from {os.path.basename(file_path)}")
            print(f"  Original: {text[:80]}...")
            
            rephrased_text = self.rephrase_with_topic_context(text)
            print(f"  Rephrased: {rephrased_text[:80]}...")
            time.sleep(self.delay)
            
            search_results = self.search_google(text, rephrased_text)
            time.sleep(self.delay)
            
            print(f"  Found {len(search_results)} links, checking relevance...")
            
            relevant_links = []
            
            for link in search_results:
                relevance_check = self.check_relevance(link, text)
                
                if relevance_check['relevant'] and relevance_check['confidence'] >= self.relevance_threshold:
                    print(f"    Relevant: {link['title'][:60]}... (confidence: {relevance_check['confidence']})")
                    print(f"      Checking trust score...")
                    
                    trust_check = self.check_trust_score(link)
                    print(f"      Trust score: {trust_check['trust_score']} ({trust_check['source_type']})")
                    
                    print(f"      Extracting content from URL...")
                    extracted_content = self.extract_content_from_url(link['link'])
                    print(f"      Extracted {len(extracted_content)} characters")
                    
                    relevant_links.append({
                        'title': link['title'],
                        'link': link['link'],
                        'snippet': link['snippet'],
                        'relevance_confidence': relevance_check['confidence'],
                        'relevance_reason': relevance_check['reason'],
                        'trust_score': trust_check['trust_score'],
                        'source_type': trust_check['source_type'],
                        'trust_reasoning': trust_check['trust_reasoning'],
                        'extracted_content': extracted_content
                    })
                else:
                    print(f"    Not relevant: {link['title'][:60]}... (confidence: {relevance_check['confidence']})")
                
                time.sleep(self.delay)
            
            results.append({
                'original_data': item,
                'search_query': text,
                'relevant_links': relevant_links,
                'relevant_count': len(relevant_links),
                'total_checked': len(search_results)
            })
        
        return {
            'source_file': os.path.basename(file_path),
            'processed_at': datetime.now().isoformat(),
            'total_items': len(data),
            'results': results
        }
    
    def process_all_files(self, data_folder: str = "data"):
        json_files = ['common.json', 'leftist.json', 'rightist.json']
        all_results = {}
        
        print("="*60)
        print("GOOGLE SEARCH + GEMINI RELEVANCE FILTER")
        print("="*60)
        print(f"\nTopic: {self.topic}")
        print(f"Links per text: {self.links_per_text}")
        print(f"Relevance threshold: {self.relevance_threshold}")
        print("="*60 + "\n")
        
        for json_file in json_files:
            file_path = os.path.join(data_folder, json_file)
            if not os.path.exists(file_path):
                print(f"Warning: {file_path} not found, skipping...\n")
                continue
            
            print(f"\nProcessing {json_file}...")
            results = self.process_json_file(file_path)
            all_results[json_file] = results
        
        processed_at = datetime.now().isoformat()
        total_relevant = 0
        
        for json_file, file_data in all_results.items():
            base_name = json_file.replace('.json', '')
            output_file = f'relevant_{base_name}.json'
            
            all_items = []
            
            for result in file_data['results']:
                bias_x = result['original_data'].get('bias_x', 0.5)
                significance_y = result['original_data'].get('significance_y', 0.5)
                combined_score = bias_x * significance_y
                
                item = {
                    'text': result['original_data'].get('text', ''),
                    'bias_x': bias_x,
                    'significance_y': significance_y,
                    'combined_score': round(combined_score, 4),
                    'color': result['original_data'].get('color', ''),
                    'relevant_links': []
                }
                
                for link in result['relevant_links']:
                    item['relevant_links'].append({
                        'title': link['title'],
                        'link': link['link'],
                        'snippet': link['snippet'],
                        'trust_score': link['trust_score'],
                        'source_type': link['source_type'],
                        'extracted_content': link['extracted_content']
                    })
                    total_relevant += 1
                
                all_items.append(item)
            
            all_items.sort(key=lambda x: x['combined_score'], reverse=True)
            
            output_data = {
                'topic': self.topic,
                'source_file': json_file,
                'processed_at': processed_at,
                'total_items': len(all_items),
                'items': all_items
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
            print(f"Saved: {output_file}")
        
        self._print_summary(all_results, total_relevant)
        
        return all_results
    
    def _print_summary(self, all_results: dict, total_relevant: int) -> None:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        for json_file, file_data in all_results.items():
            base_name = json_file.replace('.json', '')
            relevant_count = sum(len(r['relevant_links']) for r in file_data['results'])
            total_items = file_data['total_items']
            
            print(f"\n{json_file}:")
            print(f"  Total items: {total_items}")
            print(f"  Items with relevant links: {relevant_count}")
            print(f"  Output: relevant_{base_name}.json")
        
        print(f"\nTOTAL RELEVANT LINKS: {total_relevant}")
        print("="*60)
    
    def cleanup(self):
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass


def main():
    system = RelevanceSearchSystem()
    try:
        system.process_all_files()
    finally:
        system.cleanup()


if __name__ == "__main__":
    main()
