import os
import unittest
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

import bedrock_first_request as app


VALID_ENV = {
    "OPENAI_API_KEY": "dummy-test-key-not-sent",
    "OPENAI_BASE_URL": "https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1",
}


class BedrockFirstRequestTests(unittest.TestCase):
    def test_uses_chat_completions_api_with_supplied_model_and_strips_output(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="  Amazon Bedrock provides managed model access.\n"
                    )
                )
            ]
        )

        answer = app.ask_bedrock(
            client,
            "What does Amazon Bedrock provide?",
            model_id="test-model",
        )

        client.chat.completions.create.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "What does Amazon Bedrock provide?"}],
        )
        self.assertEqual(answer, "Amazon Bedrock provides managed model access.")
        self.assertEqual(app.DEFAULT_MODEL_ID, "openai.gpt-oss-20b-1:0")

    def test_strips_reasoning_block_from_output(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="<reasoning>thinking it through</reasoning>Amazon Bedrock is managed."
                    )
                )
            ]
        )

        answer = app.ask_bedrock(client, "What is Amazon Bedrock?")

        self.assertEqual(answer, "Amazon Bedrock is managed.")

    def test_rejects_blank_prompt_without_sending_request(self):
        client = Mock()

        with self.assertRaisesRegex(ValueError, "prompt must not be empty"):
            app.ask_bedrock(client, "   ")

        client.chat.completions.create.assert_not_called()

    def test_rejects_empty_model_output(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="   "))]
        )

        with self.assertRaisesRegex(RuntimeError, "empty text response"):
            app.ask_bedrock(client, "Explain Amazon Bedrock.")

    def test_accepts_regional_bedrock_runtime_endpoint(self):
        with patch.dict(os.environ, VALID_ENV, clear=True):
            app.require_configuration()

    def test_rejects_lookalike_bedrock_runtime_endpoint(self):
        invalid_env = {
            **VALID_ENV,
            "OPENAI_BASE_URL": "https://bedrock-runtime.attacker.example/openai/v1",
        }

        with patch.dict(os.environ, invalid_env, clear=True):
            with self.assertRaisesRegex(SystemExit, "CONFIG_INVALID"):
                app.require_configuration()

    def test_reports_missing_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(SystemExit, "OPENAI_API_KEY, OPENAI_BASE_URL"):
                app.require_configuration()

    def test_main_prints_answer_and_success_marker(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Bedrock answer"))]
        )

        with (
            patch.dict(os.environ, VALID_ENV, clear=True),
            patch.object(app, "OpenAI", return_value=client),
            patch("sys.stdout", new_callable=StringIO) as output,
        ):
            app.main()

        self.assertIn("Bedrock answer", output.getvalue())
        self.assertIn(
            "MODEL_RESPONSE_OK model=openai.gpt-oss-20b-1:0",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
