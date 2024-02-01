export default {
    async email(message, env, ctx) {
        const {from, to, headers, raw, rawSize} = message;

        // 1. Check the From address
        if (!/^(mail\.)?ustc\.edu\.cn$/.test(from.split('@').pop())) {
            message.setReject('Rejected: Invalid sender');
            return;
        }

        // 2. Check the To address
        const toAddress = to.split('@')[0].toLowerCase(); // Assuming 'to' is a string like "local-part@domain"
        if (!/(sc-upd-\d+-notice|sc-upd-\d+homework)/.test(toAddress)) {
            message.setReject('Rejected: Unknown recipient');
            return;
        }
        const field = toAddress.split('-')[3];
        const id = toAddress.split('-')[2];

        // convert raw (ReadableStream) to string
        const rawString = await new Response(raw).text();

        // Prepare data for the POST request
        const params = {
            credential: `${env.CF_WORKER_CREDENTIAL}`,
            id: parseInt(id),
            field: field,
            value: rawString,
            from_: from,
            timestamp: new Date().toISOString(),
        }
        console.log(params);

        // 3. Create a POST call to example.com
        const requestOptions = {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params),
        };

        try {
            const response = await fetch('https://schedule-test.tiankaima.dev/api/cf_email_worker', requestOptions);
            if (!response.ok) {
                // Handle non-2xx responses
                message.setReject(`Server responded with status: ${response.status}`);
            }
            // Optionally, process the response data
            const responseData = await response.text();
            message.setReject(`Successfully forwarded, response: ${JSON.stringify(params)}`);
        } catch (error) {
            message.setReject(`Error sending POST request: ${error}`);
        }
    },
};
