# main.py - Entry point of the application
# Handles argument parsing and orchestrates all modules

from agents.job_agent import create_job_agent


def main():
    print("🤖 Starting Robotics Job Agent...\n")

    agent = create_job_agent()

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                "Find Softwareentwickler job at ViSenSys GmbH company in Dortmund Germany."
            )
        }]
    })

    final_answer = result["messages"][-1].content
    print(final_answer)


if __name__ == "__main__":
    main()