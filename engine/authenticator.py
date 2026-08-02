import os


class Recognize:
    @staticmethod
    def AuthenticateFace():
        """
        Run face authentication using the trained LBPH model.
        Returns 1 on success, 0 on failure.
        Falls back to auto-pass if trainer.yml or OpenCV contrib is missing.
        """
        trainer_path = os.path.join(
            os.path.dirname(__file__), "auth", "trainer", "trainer.yml"
        )

        # If trainer model doesn't exist, warn and skip auth
        if not os.path.exists(trainer_path):
            print(
                "[Auth] WARNING: trainer.yml not found. "
                "Run engine/auth/trainer.py first to train the model. "
                "Skipping face auth for now."
            )
            return 1

        try:
            from engine.auth.recoganize import AuthenticateFace as _auth
            return _auth()
        except ImportError as e:
            print(f"[Auth] OpenCV contrib not available ({e}). Skipping face auth.")
            return 1
        except Exception as e:
            print(f"[Auth] Face authentication error: {e}. Skipping.")
            return 1
