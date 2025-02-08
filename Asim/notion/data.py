
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet, Action, App
import os
os.environ["OPENAI_API_KEY"] = "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"

llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")

composio_toolset = ComposioToolSet(api_key="d92q10eb8gkdkccf0f1y7o")

tools = composio_toolset.get_tools(actions=[
                                            'NOTION_CREATE_DATABASE',
                                            'NOTION_SEARCH_NOTION_PAGE',
                                            'NOTION_INSERT_ROW_DATABASE',
                                            'NOTION_ADD_PAGE_CONTENT',
                                            'NOTION_CREATE_NOTION_PAGE',
                                            'NOTION_FETCH_NOTION_BLOCK',
                                            'NOTION_FETCH_DATABASE',
                                            'NOTION_QUERY_DATABASE',
                                            'NOTION_GET_ABOUT_ME',
                                            'NOTION_LIST_USERS',
                                            'NOTION_GET_ABOUT_USER','NOTION_FETCH_COMMENTS',
                                            'NOTION_UPDATE_ROW_DATABASE',
                                            'NOTION_FETCH_ROW',
                                            'NOTION_CREATE_COMMENT',
                                            'NOTION_DELETE_BLOCK','NOTION_UPDATE_SCHEMA_DATABASE',
                                            'NOTION_ARCHIVE_NOTION_PAGE',
                                            # 'GMAIL_SEND_EMAIL',
                                            # 'GMAIL_FETCH_EMAILS',
                                            # 'GMAIL_GET_ATTACHMENT','GMAIL_GET_PROFILE',
                                            # 'GMAIL_CREATE_EMAIL_DRAFT',
                                            # 'GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID',
                                            # 'GMAIL_FETCH_MESSAGE_BY_THREAD_ID',
                                            # 'GMAIL_ADD_LABEL_TO_EMAIL','GMAIL_MODIFY_THREAD_LABELS',
                                            # 'GMAIL_REPLY_TO_THREAD',
                                            # 'GMAIL_LIST_THREADS','GMAIL_LIST_LABELS','GMAIL_CREATE_LABEL','GMAIL_GET_PEOPLE','GMAIL_SEARCH_PEOPLE',
                                            # 'GMAIL_GET_CONTACTS','GMAIL_REMOVE_LABEL','GOOGLECALENDAR_FIND_EVENT',
                                            # 'GOOGLECALENDAR_CREATE_EVENT','GOOGLECALENDAR_FIND_FREE_SLOTS','GOOGLECALENDAR_GET_CURRENT_DATE_TIME',
                                            # 'GOOGLECALENDAR_LIST_CALENDARS',
                                            # 'GOOGLECALENDAR_QUICK_ADD',
                                            # 'GOOGLECALENDAR_GET_CALENDAR',
                                            # 'GOOGLECALENDAR_DELETE_EVENT',
                                            # 'GOOGLECALENDAR_UPDATE_EVENT',
                                            # 'GOOGLECALENDAR_PATCH_CALENDAR',
                                            # 'GOOGLECALENDAR_DUPLICATE_CALENDAR',
                                            # 'GOOGLECALENDAR_REMOVE_ATTENDEE',
                                            
                                            # 'GOOGLEDRIVE_FIND_FILE','GOOGLEDRIVE_CREATE_FILE_FROM_TEXT',
                                            # 'GOOGLEDRIVE_FIND_FOLDER','GOOGLEDRIVE_CREATE_FOLDER',
                                            # 'GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE','GOOGLEDRIVE_UPLOAD_FILE',
                                            # 'GOOGLEDRIVE_EDIT_FILE','GOOGLEDRIVE_COPY_FILE',
                                            # 'GOOGLEDRIVE_DELETE_FOLDER_OR_FILE','GOOGLEDRIVE_DOWNLOAD_FILE',
                                            # 'GOOGLESHEETS_BATCH_GET',
                                            # 'GOOGLESHEETS_GET_SPREADSHEET_INFO',
                                            # 'GOOGLESHEETS_BATCH_UPDATE',
                                            # 'GOOGLESHEETS_CREATE_GOOGLE_SHEET1',
                                            # 'GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW',
                                            # 'GOOGLESHEETS_SHEET_FROM_JSON',
                                            # 'GOOGLESHEETS_CLEAR_VALUES',
                                           
                                           
                                            # 'OUTLOOK_OUTLOOK_GET_MESSAGE',
                                            # 'OUTLOOK_OUTLOOK_LIST_MESSAGES',
                                            # 'OUTLOOK_OUTLOOK_GET_EVENT',
                                            # 'OUTLOOK_OUTLOOK_GET_PROFILE',
                                            # 'OUTLOOK_LIST_OUTLOOK_ATTACHMENTS',
                                            # 'OUTLOOK_OUTLOOK_CALENDAR_CREATE_EVENT',
                                            # 'OUTLOOK_OUTLOOK_SEND_EMAIL','OUTLOOK_OUTLOOK_CREATE_DRAFT',
                                            # 'OUTLOOK_OUTLOOK_GET_SCHEDULE','OUTLOOK_OUTLOOK_LIST_EVENTS',
                                            # 'OUTLOOK_DOWNLOAD_OUTLOOK_ATTACHMENT','OUTLOOK_OUTLOOK_GET_CONTACT','OUTLOOK_OUTLOOK_CREATE_DRAFT_REPLY',
                                            # 'OUTLOOK_OUTLOOK_SEARCH_MESSAGES','OUTLOOK_OUTLOOK_LIST_CONTACTS','OUTLOOK_OUTLOOK_UPDATE_CALENDAR_EVENT',
                                            # 'OUTLOOK_OUTLOOK_REPLY_EMAIL','OUTLOOK_OUTLOOK_CREATE_CONTACT','OUTLOOK_OUTLOOK_DELETE_EVENT','OUTLOOK_OUTLOOK_UPDATE_CONTACT',
                                            # 'GOOGLEDOCS_CREATE_DOCUMENT','GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT','GOOGLEDOCS_GET_DOCUMENT_BY_ID','GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN',
                                            # 'GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN',
                                            # 'FIRECRAWL_SCRAPE_EXTRACT_DATA_LLM','FIRECRAWL_CRAWL_URLS','FIRECRAWL_EXTRACT','FIRECRAWL_MAP_URLS','FIRECRAWL_CANCEL_CRAWL_JOB',
                                            # 'FIRECRAWL_CRAWL_JOB_STATUS',
                                            # 'GOOGLEPHOTOS_BATCH_GET_MEDIA_ITEMS',
                                            # 'GOOGLEPHOTOS_BATCH_ADD_MEDIA_ITEMS','GOOGLEPHOTOS_CREATE_ALBUM',
                                            # 'GOOGLEPHOTOS_UPDATE_MEDIA_ITEM','GOOGLEPHOTOS_GET_MEDIA_ITEM_DOWNLOAD',
                                            # 'GOOGLEPHOTOS_LIST_ALBUMS','GOOGLEPHOTOS_SEARCH_MEDIA_ITEMS','GOOGLEPHOTOS_LIST_MEDIA_ITEMS','GOOGLEPHOTOS_BATCH_CREATE_MEDIA_ITEMS','GOOGLEPHOTOS_GET_ALBUM',
                                            # 'GOOGLEPHOTOS_ADD_ENRICHMENT','GOOGLEPHOTOS_UPLOAD_MEDIA'
                                            #'GOOGLEMEET_CREATE_MEET'
                                        #     ,'GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID','GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET','GOOGLEMEET_GET_MEET','GOOGLEMEET_CREATE_MEET',
                                        #    'YOUTUBE_SEARCH_YOU_TUBE','YOUTUBE_VIDEO_DETAILS','YOUTUBE_LIST_CAPTION_TRACK','YOUTUBE_LIST_CHANNEL_VIDEOS','YOUTUBE_LOAD_CAPTIONS','YOUTUBE_LIST_USER_SUBSCRIPTIONS','YOUTUBE_LIST_USER_PLAYLISTS','YOUTUBE_SUBSCRIBE_CHANNEL','YOUTUBE_UPDATE_VIDEO','YOUTUBE_UPDATE_THUMBNAIL'
                                        #     ,'LINKEDIN_GET_MY_INFO',
                                        #     'LINKEDIN_CREATE_LINKED_IN_POST','LINKEDIN_GET_COMPANY_INFO','LINKEDIN_DELETE_LINKED_IN_POST'
                                            ])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

task = "fetch me all rows of the database with database id: 194017e1ad4d81d597f4c30cec36fdc6"
result = agent_executor.invoke({"input": task})
print(result)
