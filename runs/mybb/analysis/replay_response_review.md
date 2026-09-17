# MyBB replay response review

- Reviewed: 14
- Vulnerable after review: 2
- Not vulnerable after review: 12

## `newthread.php` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: New Thread in My Forum
- Reason: newthread.php response is normal forum/category/password handling, not the target vulnerability

Excerpt:

```text
New Thread in My Forum Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / My Category / My Forum / New Thread Post a new Thread Username: user1 [ change user ] Thread Subject Post Icon: no icon Your Message: Smilies Post Options: Signature: include your signature. (registered users only) Disable Smilies: disable smilies from showing in this post. Thread Subscription: Specify the type of email notification and thread subscription you'd like to have to this thread. (Registered users only) Do not subscribe to this thread Subscribe without receiving email notification of new replies Subscribe and 
```

## `newthread.php` / actor `user2`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: New Thread in My Forum
- Reason: newthread.php response is normal forum/category/password handling, not the target vulnerability

Excerpt:

```text
New Thread in My Forum Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user2 . You last visited: 06-26-2026, 09:46 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / My Category / My Forum / New Thread Post a new Thread Username: user2 [ change user ] Thread Subject Post Icon: no icon Your Message: Smilies Post Options: Signature: include your signature. (registered users only) Disable Smilies: disable smilies from showing in this post. Thread Subscription: Specify the type of email notification and thread subscription you'd like to have to this thread. (Registered users only) Do not subscribe to this thread Subscribe without receiving email notification of new replies Subscribe and 
```

## `newthread.php?fid=p1&processed=p1` / actor `visitor`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: newthread.php response is normal forum/category/password handling, not the target vulnerability

Excerpt:

```text
Forums Search Member List Calendar Help Current time: 07-04-2026, 04:16 PM Hello There, Guest! ( Login — Register ) Forums / Board Message Forums Invalid forum English (American) Contact Us | Your Website | Return to Top | Return to Content | Lite (Archive) Mode | RSS Syndication Powered By MyBB , © 2002-2026 MyBB Group .
```

## `newthread.php?fid=p1&processed=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: newthread.php response is normal forum/category/password handling, not the target vulnerability

Excerpt:

```text
Forums Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Board Message Forums Invalid forum English (American) Contact Us | Your Website | Return to Top | Return to Content | Lite (Archive) Mode | RSS Syndication Powered By MyBB , © 2002-2026 MyBB Group .
```

## `newthread.php?fid=p1&processed=p1` / actor `user2`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: newthread.php response is normal forum/category/password handling, not the target vulnerability

Excerpt:

```text
Forums Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user2 . You last visited: 06-26-2026, 09:46 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Board Message Forums Invalid forum English (American) Contact Us | Your Website | Return to Top | Return to Content | Lite (Archive) Mode | RSS Syndication Powered By MyBB , © 2002-2026 MyBB Group .
```

## `private.php?action=delete&pmid=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: private.php page is an authenticated user feature or invalid PM target, not the known forum-password subscription bug

Excerpt:

```text
Forums Forums The selected private messages have been deleted.jG8a7UwZg9 Click here if you don't want to wait any longer.
```

## `private.php?action=read&pmid=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: private.php page is an authenticated user feature or invalid PM target, not the known forum-password subscription bug

Excerpt:

```text
Forums Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Board Message Forums Invalid PMLwVKziAC31 English (American) Contact Us | Your Website | Return to Top | Return to Content | Lite (Archive) Mode | RSS Syndication Powered By MyBB , © 2002-2026 MyBB Group .
```

## `private.php?action=send&do=forward&pmid=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Compose a Private MessageAVk90BMwuo
- Reason: private.php page is an authenticated user feature or invalid PM target, not the known forum-password subscription bug

Excerpt:

```text
Compose a Private MessageAVk90BMwuo Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Private MessagesLQeGcs6OW7 / ComposecRfJ04MBtO Menu User CP Home Messenger Compose Inbox Sent Items Drafts Trash Can Tracking Edit Folders Your Profile Edit Profile Change Password Change Email Change Avatar Change Signature Edit Options Miscellaneous Group Memberships Buddy/Ignore List Manage Attachments Saved Drafts Subscribed Threads Forum Subscriptions View Profile Compose a Private MessageAVk90BMwuo Recipients:okI9s2UycT Separate multiple user names with a comma.3eqV4oEAd2 You may send this message to a
```

## `private.php?action=send&do=reply&pmid=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Compose a Private MessageAVk90BMwuo
- Reason: private.php page is an authenticated user feature or invalid PM target, not the known forum-password subscription bug

Excerpt:

```text
Compose a Private MessageAVk90BMwuo Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Private MessagesLQeGcs6OW7 / ComposecRfJ04MBtO Menu User CP Home Messenger Compose Inbox Sent Items Drafts Trash Can Tracking Edit Folders Your Profile Edit Profile Change Password Change Email Change Avatar Change Signature Edit Options Miscellaneous Group Memberships Buddy/Ignore List Manage Attachments Saved Drafts Subscribed Threads Forum Subscriptions View Profile Compose a Private MessageAVk90BMwuo Recipients:okI9s2UycT Separate multiple user names with a comma.3eqV4oEAd2 You may send this message to a
```

## `private.php?fid=p1` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums - Private MessagingLyrn29cBi5
- Reason: private.php page is an authenticated user feature or invalid PM target, not the known forum-password subscription bug

Excerpt:

```text
Forums - Private MessagingLyrn29cBi5 Search Member List Calendar Help Current time: 07-04-2026, 06:16 AM Welcome back, user1 . You last visited: 06-27-2026, 08:16 AM ( User CP — Log Out ) Open Buddy List View New Posts | View Today's Posts | Private Messages (Unread 0, Total 0) Forums / Private MessagesLQeGcs6OW7 Menu User CP Home Messenger Compose Inbox Sent Items Drafts Trash Can Tracking Edit Folders Your Profile Edit Profile Change Password Change Email Change Avatar Change Signature Edit Options Miscellaneous Group Memberships Buddy/Ignore List Manage Attachments Saved Drafts Subscribed Threads Forum Subscriptions View Profile 0% of PM space used.EIc9qZaSKX InboxN4twmVP9k0 | Compose MessagexFXALQSDM7 | Manage Foldersiequc9ASPV | Empty FoldersM4jNZQwBia | Download MessagesxkjRDnBGf3 ( 
```

## `usercp2.php` / actor `user1`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: bare usercp2.php action endpoint; not a distinct access-control page

Excerpt:

```text
Forums Forums The selected thread has been added to your subscriptions list. You will now be returned to the location you came from. Click here if you don't want to wait any longer.
```

## `usercp2.php` / actor `user2`

- Original: vulnerable
- Review: not_vulnerable
- HTTP: 200
- Title: Forums
- Reason: bare usercp2.php action endpoint; not a distinct access-control page

Excerpt:

```text
Forums Forums The selected thread has been added to your subscriptions list. You will now be returned to the location you came from. Click here if you don't want to wait any longer.
```

## `usercp2.php?action=addsubscription&fid=p1&type=forum` / actor `user1`

- Original: vulnerable
- Review: vulnerable
- HTTP: 200
- Title: Forums
- Reason: known target: logged-in user can subscribe to password-protected forum without entering forum password

Excerpt:

```text
Forums Forums The selected forum has been added to your forum subscriptions list. You will now be returned to where you came from. Click here if you don't want to wait any longer.
```

## `usercp2.php?action=addsubscription&fid=p1&type=forum` / actor `user2`

- Original: vulnerable
- Review: vulnerable
- HTTP: 200
- Title: Forums
- Reason: known target: logged-in user can subscribe to password-protected forum without entering forum password

Excerpt:

```text
Forums Forums The selected forum has been added to your forum subscriptions list. You will now be returned to where you came from. Click here if you don't want to wait any longer.
```
