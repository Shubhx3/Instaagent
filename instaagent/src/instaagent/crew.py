from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os

# Import the custom tools
from instaagent.tools.auth_tools import InstagramAuthTool, InstagramRefreshTokenTool
from instaagent.tools.subscription_tools import InstagramSubscriptionTool
from instaagent.tools.content_tools import InstagramPostTool, InstagramCaptionTool

# Load environment variables
load_dotenv()

@CrewBase
class Instaagent():
    """Instaagent crew"""

    # YAML configuration files for agents and tasks
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Define Agents
    @agent
    def insta_auth_agent(self) -> Agent:
        """Define an agent for handling Instagram authentication-related tasks."""
        return Agent(
            config=self.agents_config['insta_auth_agent'],
            verbose=True,
            tools=[
                InstagramAuthTool(),  # Handles authentication and token refresh
                InstagramRefreshTokenTool()  # Refreshes the access token when needed
            ]
        )

    @agent
    def insta_subscription_agent(self) -> Agent:
        """
        Define an agent for handling Instagram subscription-related tasks.
        """
        return Agent(
            config=self.agents_config['insta_subscription_agent'],
            verbose=True,
            tools=[
                InstagramSubscriptionTool()  # Handles subscription-related tasks
            ]
        )

    @agent
    def insta_post_agent(self) -> Agent:
        """
        Define an agent for handling Instagram post-related tasks.
        
        This agent is responsible for scheduling posts and generating captions
        using the provided tools.
        """
        return Agent(
            config=self.agents_config['insta_post_agent'],
            verbose=True,
            tools=[
                InstagramPostTool(),  # Schedules Instagram posts
                InstagramCaptionTool()  # Generates captions for posts
            ]
        )

    # Define Tasks
    @task
    def authenticate_user(self) -> Task:
        """
        Define a task to authenticate the user with the Instagram API.

        This task will initiate the OAuth flow and exchange the authorization
        code for an access token and refresh token. The tokens will be stored
        securely and used for subsequent API requests.

        :return: A Task object with the agent and config set for the authentication task.
        """
        return Task(
            config=self.tasks_config['authenticate_user'],
            agent=self.insta_auth_agent
        )

    @task
    def refresh_token(self) -> Task:
        """
        Define a task to refresh the access token.

        This task will check if the access token needs to be refreshed (i.e., if
        it is close to expiring). If so, it will use the refresh token to get a
        new access token and store it securely.

        :return: A Task object with the agent and config set for the token refresh task.
        """
        return Task(
            config=self.tasks_config['refresh_token'],
            agent=self.insta_auth_agent
        )

    @task
    def subscribe_to_hashtags(self) -> Task:
        """
        Define a task to subscribe to Instagram hashtags.

        This task will use the Instagram API to subscribe to the hashtags specified
        in the config. The task is assigned to the `insta_subscription_agent`.
        """
        return Task(
            config=self.tasks_config['subscribe_to_hashtags'],
            agent=self.insta_subscription_agent
        )

    @task
    def schedule_post(self) -> Task:
        """
        Define a task to schedule Instagram posts.

        This task uses the `insta_post_agent` to handle scheduling of posts
        at optimal times. It retrieves the configuration from the task config.

        :return: A Task object with the agent and config set for scheduling posts.
        """
        return Task(
            config=self.tasks_config['schedule_post'],
            agent=self.insta_post_agent
        )

    @task
    def generate_caption(self) -> Task:
        """
        Define a task to generate an Instagram caption.

        This task utilizes the `insta_post_agent` to generate captions based
        on the provided configuration. It leverages the InstagramCaptionTool
        for creating engaging captions tailored to the post topic and tone.

        :return: A Task object with the agent and config set for generating captions.
        """
        return Task(
            config=self.tasks_config['generate_caption'],
            agent=self.insta_post_agent
        )

    # Assemble the Crew
    @crew
    def crew(self) -> Crew:
        """
        Assemble the crew with defined agents and tasks.

        This method sets up the crew by specifying the agents and tasks
        that will be executed. The process is set to sequential, meaning
        that tasks will be executed one after the other.

        :return: A Crew object with the agents, tasks, and process set.
        """
        return Crew(
            agents=[
                self.insta_auth_agent,  # Agent for handling authentication
                self.insta_subscription_agent,  # Agent for managing subscriptions
                self.insta_post_agent  # Agent for post scheduling and caption creation
            ],
            tasks=[
                self.authenticate_user,  # Task for user authentication
                self.refresh_token,  # Task for refreshing access tokens
                self.subscribe_to_hashtags,  # Task for subscribing to hashtags
                self.schedule_post,  # Task for scheduling Instagram posts
                self.generate_caption  # Task for generating post captions
            ],
            process=Process.sequential,  # Execute tasks sequentially
            verbose=True,  # Enable verbose output for debugging
        )
