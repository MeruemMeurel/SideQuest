from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from social.models import Comment, Follow, Like, Post


User = get_user_model()


class Command(BaseCommand):
    help = "Create reproducible SideQuest demo users and social data."

    def handle(self, *args, **options):
        standard_group, _ = Group.objects.get_or_create(name="standard_users")
        moderators_group, _ = Group.objects.get_or_create(name="moderators")

        users = {
            "user_demo": self.create_or_update_user(
                username="user_demo",
                password="user12345",
                email="user_demo@example.com",
                bio="Weekend quest log: coffee, code, and a suspiciously tiny bonsai.",
                groups=(standard_group,),
            ),
            "alice_demo": self.create_or_update_user(
                username="alice_demo",
                password="alice12345",
                email="alice_demo@example.com",
                bio="Needlework, tiny builds, and a very Arya-like habit of finishing lists.",
                groups=(standard_group,),
            ),
            "bob_demo": self.create_or_update_user(
                username="bob_demo",
                password="bob12345",
                email="bob_demo@example.com",
                bio="Paints miniatures slowly. Blames the Emperor when the primer goes weird.",
                groups=(standard_group,),
            ),
            "moderator_demo": self.create_or_update_user(
                username="moderator_demo",
                password="moderator12345",
                email="moderator_demo@example.com",
                bio="Keeps the realm civil, one deleted hot take at a time.",
                groups=(moderators_group,),
            ),
            "admin_demo": self.create_or_update_user(
                username="admin_demo",
                password="admin12345",
                email="admin_demo@example.com",
                bio="Admin of the Seven Side Quests.",
                is_staff=True,
                is_superuser=True,
            ),
        }

        post_specs = [
            ("user_demo", "I tried to build a shelf and accidentally invented a leaning tower for mugs."),
            ("user_demo", "Today I named my study timer Ser Pings-a-lot because it keeps demanding honor."),
            ("user_demo", "My sourdough starter rose like it heard a dragon was coming."),
            ("alice_demo", "Painted a tiny raven on a bookmark. It now looks like it knows too much."),
            ("alice_demo", "Knitted three rows, dropped one stitch, negotiated peace, then dropped another."),
            ("alice_demo", "My garden labels are now written like quest objectives. The basil approves."),
            ("alice_demo", "I made a model bridge from coffee stirrers. It holds exactly one dramatic pause."),
            ("bob_demo", "Dry-brushed a Space Marine and immediately understood why patience is a virtue."),
            ("bob_demo", "The Warhammer pile of shame has gained sentience and asked for better lighting."),
            ("bob_demo", "My chess puzzle streak survived, but only because the knight did all the politics."),
            ("bob_demo", "Fixed my bike chain. It rewarded me by teaching my jeans about grease."),
            ("moderator_demo", "Reminder: side quests are welcome, personal duels are not."),
            ("moderator_demo", "Organized my desk. Found two pens, one cable, and the lost banner of House USB."),
            ("user_demo", "I practiced guitar until the cat filed a noise complaint with the small council."),
            ("alice_demo", "Started a tiny herbarium. Every pressed leaf looks like evidence in a fantasy trial."),
            ("bob_demo", "Painted hazard stripes for an hour. The Imperium may be eternal; my wrist is not."),
        ]

        posts = [
            self.get_or_create_post(
                author=users[username],
                content=content,
            )
            for username, content in post_specs
        ]

        follow_specs = [
            ("user_demo", "alice_demo"),
            ("user_demo", "bob_demo"),
            ("alice_demo", "user_demo"),
            ("alice_demo", "bob_demo"),
            ("bob_demo", "alice_demo"),
            ("moderator_demo", "user_demo"),
        ]

        for follower, followed in follow_specs:
            Follow.objects.get_or_create(
                follower=users[follower],
                followed=users[followed],
            )

        like_specs = [
            ("user_demo", 3),
            ("user_demo", 4),
            ("user_demo", 7),
            ("user_demo", 8),
            ("alice_demo", 0),
            ("alice_demo", 2),
            ("alice_demo", 8),
            ("alice_demo", 10),
            ("bob_demo", 0),
            ("bob_demo", 1),
            ("bob_demo", 3),
            ("bob_demo", 4),
            ("bob_demo", 14),
            ("moderator_demo", 0),
            ("moderator_demo", 5),
            ("moderator_demo", 8),
            ("moderator_demo", 11),
            ("admin_demo", 7),
            ("admin_demo", 12),
            ("admin_demo", 15),
        ]

        for username, post_index in like_specs:
            Like.objects.get_or_create(
                user=users[username],
                post=posts[post_index],
            )

        comment_specs = [
            ("alice_demo", 0, "This shelf deserves its own safety inspection and maybe a bard."),
            ("bob_demo", 0, "Add purity seals. It works for tanks, probably works for furniture."),
            ("user_demo", 3, "That raven is absolutely judging my browser tabs."),
            ("moderator_demo", 4, "Peace negotiations with yarn are valid project management."),
            ("alice_demo", 7, "The dry brush chooses the painter, not the other way around."),
            ("user_demo", 8, "If it asks for snacks, do not feed it sprues after midnight."),
            ("bob_demo", 12, "House USB always returns when you stop looking."),
            ("admin_demo", 11, "Pinned in spirit. Duels remain out of scope."),
            ("alice_demo", 13, "The cat is right, but the small council is overreacting."),
            ("bob_demo", 14, "A fantasy trial still needs chain of custody for leaves."),
            ("user_demo", 15, "Hazard stripes are just anxiety with better contrast."),
            ("moderator_demo", 2, "Dragon-adjacent baking is still baking."),
        ]

        for username, post_index, content in comment_specs:
            Comment.objects.get_or_create(
                author=users[username],
                post=posts[post_index],
                content=content,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded demo data: "
                f"{User.objects.filter(username__in=users.keys()).count()} users, "
                f"{Post.objects.filter(author__username__in=users.keys()).count()} posts, "
                f"{Follow.objects.filter(follower__username__in=users.keys()).count()} follows, "
                f"{Like.objects.filter(user__username__in=users.keys()).count()} likes, "
                f"{Comment.objects.filter(author__username__in=users.keys()).count()} comments."
            )
        )

    def create_or_update_user(
        self,
        username,
        password,
        email,
        bio,
        groups=(),
        is_staff=False,
        is_superuser=False,
    ):
        user, _ = User.objects.get_or_create(username=username)
        user.email = email
        user.bio = bio
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()

        if groups:
            user.groups.set(groups)

        return user

    def get_or_create_post(self, author, content):
        post, _ = Post.objects.get_or_create(
            author=author,
            content=content,
        )
        return post
