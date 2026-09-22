# Talk Notes: "Self-Care on Rails" (RailsConf 2021)

At RailsConf 2021, Ben Greenberg’s talk “[Self-Care on Rails](https://www.youtube.com/watch?v=7uuRV17e8gg)” explored what developers could do when the pandemic made ordinary family life extraordinarily difficult.

This was not a talk about squeezing more productivity from an exhausted brain. It was about using familiar technical skills to care for ourselves and the people closest to us.

## Self-care is not selfish

Greenberg begins with a broader question: What responsibility do technologists have for the effects of their work?

Software is not neutral. Code can reinforce harmful systems, but it can also reduce frustration, create moments of connection, and make life slightly more manageable. Initiatives such as the Hippocratic License reflect a growing awareness that developers should consider how their work affects other people.

That responsibility does not exclude the developer. The saying “If I am not for myself, who will be for me?” frames self-interest as something healthier than selfishness. Our needs exist alongside everyone else’s, and they matter too.

This distinction became especially important during the pandemic. Adults and children experienced isolation, uncertainty, and disruption. Greenberg responded with what he knew: building software.

## A birthday party built with Rails

When an in-person celebration was impossible, Greenberg built a virtual watch-party application for his son’s ninth birthday.

The application used Ruby on Rails and the Vonage Video API to let children gather remotely. Behind the API was WebRTC, an open standard that enables browsers to exchange video, audio, and other data in real time.

Rails handled the application, but the browser still required JavaScript. As Greenberg joked, you cannot escape JavaScript—even at RailsConf.

The most interesting part of this project was not its architecture. It was the reason for its existence. The application was deliberately small, personal, and temporary. It did not need to become a startup or attract thousands of users. Its success metric was giving one child a happier birthday.

That is a useful correction to the way developers often discuss side projects. A project can be worthwhile simply because it helps someone we love.

## Automating an exhausting routine

Greenberg also described automating the daily health declarations required by his children’s school.

The original routine involved signing in, selecting each child, checking boxes, adding a signature, and submitting the form. Repeating that every morning added one more obligation to an already stressful schedule.

Using Ruby and [Watir](https://dev.to/bengreenberg/automate-school-forms-with-web-scraping-in-ruby-2c3j), Greenberg created a script that controlled a browser, completed the declarations, skipped forms already submitted, and reported whether the process succeeded.

This was not automation for automation’s sake. It removed a small but persistent source of friction. Saving a few minutes each morning created more space for his family—and for himself.

## My biggest takeaway

“Self-Care on Rails” presents programming as a practical form of care.

Developers often imagine impact at enormous scale: millions of requests, worldwide platforms, or open-source projects used by entire industries. Greenberg reminds us that impact can also be intensely local. An application serving one family may still be valuable.

The talk also challenges the idea that caring for ourselves competes with caring for others. The two can reinforce each other. Reducing our own stress can make us more patient, available, and capable of helping the people around us.

The next useful project may not be a portfolio piece or a business. It may be a tiny tool that removes one recurring annoyance, restores one missed experience, or gives someone we care about a little more room to breathe.

That is still meaningful software. Perhaps it is some of the most meaningful software we can build.

#rails #ruby #webdev #mentalhealth