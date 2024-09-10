from langchain_community.llms import Ollama
from bs4 import BeautifulSoup
import requests


def remove_tags(html):

    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

#this method basically gets all the content from a part
def getPart():
   url = "https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title18-chapter1&num=0&saved=L3ByZWxpbUB0aXRsZTE4L3BhcnQx%7CZ3JhbnVsZWlkOlVTQy1wcmVsaW0tdGl0bGUxOC1wYXJ0MQ%3D%3D%7C%7C%7C0%7Cfalse%7Cprelim"
   page = requests.get(url)
   pageText = remove_tags(page.content)
   return pageText
  #  f = open("part1Content.txt", "w")
  #  f.write(pageText)
  #  f.close()



def getSectionInfo(sectionStart, sectionEnd, legalSections):
  for sec in range(sectionStart, sectionEnd+1):
    sectionURL = "https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title18-section" + str(sec) + "&num=0&saved=%7CZ3JhbnVsZWlkOlVTQy1wcmVsaW0tdGl0bGUxOC1zZWN0aW9uNw%3D%3D%7C%7C%7C0%7Cfalse%7Cprelim"
    page = requests.get(sectionURL)
    soup = BeautifulSoup(page.content, "html.parser")
    sectionTitle = soup.title.string
    if ("Repealed" not in sectionTitle):
      legalSectionTitle = "Section " + str(sec) + ": " + sectionTitle
      sectionDescription = soup.find_all("p", class_='statutory-body')
      legalSectionDescription = "Section " + str(sec) + ": "
      for item in sectionDescription:
        legalSectionDescription += item.text
        legalSectionDescription += "\n"
      legalSections[legalSectionTitle] = legalSectionDescription
    else:
      continue

   

def getAllSectionHeaders():
  sectionTitles = []
  url = "https://uscode.house.gov/view.xhtml?path=/prelim@title18/part1&edition=prelim"
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  titleTags = soup.find_all("h3", class_="section-head")
  for title in titleTags:
    sectionTitles.append(title.text)
  return sectionTitles 

def generateMistralResponse(extractedText):
    prompt = f"""
      Text:
      {extractedText}

      Instruction:
      For each section from 1 to 27 provided in the text, do the following:
      1. Generate a question based only on the section's content.
      2. Provide the answer to the question, based strictly on the section's information.
      3. Format the response as a Python list, where each item is a dictionary with:
        - A key "instruction" containing the generated question.
        - A key "value" containing the corresponding answer.

      Ensure that every section is covered and no information is drawn from outside the provided text.

      Example output:
      [
          {{
              "instruction": "What is the maximum penalty for being an accessory after the fact under Section 3?",
              "value": "An accessory after the fact can be imprisoned for up to half of the principal's punishment, or up to 15 years if the principal is punishable by life imprisonment or death."
          }},
          {{
              "instruction": "What is defined as 'United States' in Section 5 of Title 18?",
              "value": "The term 'United States' includes all places and waters subject to U.S. jurisdiction, except the Canal Zone."
          }}
      ]
      """




    llm = Ollama(model="mistral")
    llmResponse = llm.invoke(prompt)
    return llmResponse
    


def main():
  legalSections = {}
  legalSectionsContent = ""
  getSectionInfo(1,27, legalSections)
  for title, content in list(legalSections.items()):
    content = f"Title: {title}\nContent: {content}\n"
    legalSectionsContent += content
  #generating content
  llmResponse = generateMistralResponse(legalSectionsContent)
  print(llmResponse)


   


if __name__=="__main__":
    main()

