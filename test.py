import language_tool_python
tool = language_tool_python.LanguageTool('ru-RU')
 
text = """как долго ожидать талона на высокотехнологическу помощь"""
 
# get the matches
matches = tool.check(text)
 
print(matches)