from selenium.webdriver.support.events import AbstractEventListener

class EventListener(AbstractEventListener):
    def after_navigate_to(self, url, driver):
        driver.execute_script(
            '''
            window.notifications = []
            window.Notification = class Notify extends window.Notification {
                constructor(...args) {
                    //super(...args)
                    //console.log(...args)
                    const title = args[0]
                    const options = {title, ...args[1]}
                    window.notifications.push(options)
                }
            }
            '''
        )
