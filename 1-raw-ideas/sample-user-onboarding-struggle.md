# User Onboarding Challenge

Been thinking about our signup flow after watching users struggle in yesterday's session. We're losing 40% of people in the first step - that's brutal.

The problem seems to be information overload. We're asking for:
- Email + password (fine)
- Company name and size (maybe necessary?)
- Role and department (probably overkill)
- Use case selection from 8 options (definitely too much)
- Integration preferences (way too early)

Watched how Stripe does it - they basically ask for email and you're in. Everything else happens progressively as you need it.

But our sales team is freaking out about losing lead qualification data. They want to know company size and role upfront for their scoring algorithm.

Need to find a middle ground. Maybe we can:
1. Start with just email/password
2. Add one contextual question based on their domain
3. Let everything else be optional with smart defaults
4. Use behavioral data instead of form fields where possible

The real insight: users don't care about our internal processes. They want to get to value as fast as possible.

Metrics to track:
- First step completion rate (currently 60%)
- Full signup completion (currently 24%) 
- Time to first value
- Sales qualified lead rate