import emailjs from "@emailjs/browser";

const SERVICE_ID = "service_hezo1dp";
const TEMPLATE_ID = "template_kdno1ri";
const PUBLIC_KEY = "deNfUoB8EuHjz_OiN";

export const sendNotificationEmail = async ({
    to_name,
    to_email,
    message,
    notification_type,
    notification_time,
}) => {
    try {
        const templateParams = {
            to_name,
            to_email,
            message,
            notification_type,
            notification_time,
        };

        const response = await emailjs.send(
            SERVICE_ID,
            TEMPLATE_ID,
            templateParams,
            PUBLIC_KEY
        );

        console.log("EmailJS success:", response);

        return {
            success: true,
            response,
        };
    } catch (error) {
        console.error("EmailJS error:", error);

        return {
            success: false,
            error,
        };
    }
};

