import sys
import datetime
import dateutil.parser
from nabcommon.nabservice import NabInfoCachedService
import logging
from . import aqicn


class NabAirqualityd(NabInfoCachedService):

    MESSAGES = ["bad", "moderate", "good"]
    ANIMATION_1 = (
        '{"tempo":42,"colors":['
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"000000","center":"000000","right":"000000"}]}'
    )
    ANIMATION_2 = (
        '{"tempo":14,"colors":['
        '{"left":"000000","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"000000"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"000000","right":"00ffff"},'
        '{"left":"000000","center":"000000","right":"00ffff"},'
        '{"left":"000000","center":"000000","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"000000"},'
        '{"left":"00ffff","center":"000000","right":"00ffff"},'
        '{"left":"000000","center":"00ffff","right":"00ffff"}]}'
    )
    ANIMATION_3 = (
        '{"tempo":14,"colors":['
        '{"left":"000000","center":"00ffff","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"00ffff","center":"000000","right":"000000"},'
        '{"left":"000000","center":"000000","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"00ffff"},'
        '{"left":"000000","center":"000000","right":"000000"},'
        '{"left":"00ffff","center":"00ffff","right":"000000"},'
        '{"left":"00ffff","center":"00ffff","right":"00ffff"},'
        '{"left":"000000","center":"000000","right":"00ffff"},'
        '{"left":"00ffff","center":"000000","right":"000000"},'
        '{"left":"000000","center":"00ffff","right":"000000"},'
        '{"left":"000000","center":"000000","right":"000000"},'
        '{"left":"00ffff","center":"000000","right":"00ffff"},'
        '{"left":"000000","center":"00ffff","right":"000000"}]}'
    )

    ANIMATIONS = [ANIMATION_3, ANIMATION_2, ANIMATION_1]

    def __init__(self):
        self.index_airquality = 0
        super().__init__()

    def get_config(self):
        from . import models

        config = models.Config.load()
        return (
            config.next_performance_date,
            config.next_performance_type,
            config.index_airquality,
        )

    def update_next(self, next_date, next_args):
        from . import models

        config = models.Config.load()
        config.next_performance_date = next_date
        config.next_performance_type = next_args
        config.save()

    def fetch_info_data(self, index_airquality):
        client = aqicn.aqicnClient(index_airquality)
        client.update()

        # Save inferred localization to configuration for display on web
        # interface
        from . import models

        config = models.Config.load()
        new_city = client.get_city()
        if new_city != config.localisation:
            config.localisation = new_city
            config.save()

        return client.get_data()

    def get_animation(self, info_data):
        if info_data is None:
            return None
        info_animation = NabAirqualityd.ANIMATIONS[info_data]
        return info_animation

    def perform_additional(self, expiration, type, info_data, config_t):
        if type == "today":
            message = NabAirqualityd.MESSAGES[info_data]
            packet = (
                '{"type":"message",'
                '"signature":{"audio":["nabairqualityd/signature.mp3"]},'
                '"body":[{"audio":["nabairqualityd/' + message + '.mp3"]}],'
                '"expiration":"' + expiration.isoformat() + '"}\r\n'
            )
            self.writer.write(packet.encode("utf8"))

    async def process_nabd_packet(self, packet):
        if (
            packet["type"] == "asr_event"
            and packet["nlu"]["intent"] == "airquality_forecast"
        ):
            next_date, next_args, config = self.get_config()
            now = datetime.datetime.now(datetime.timezone.utc)
            expiration = now + datetime.timedelta(minutes=1)
            info_data = self.fetch_info_data(config)
            self.perform_additional(expiration, "today", info_data, config)


if __name__ == "__main__":
    NabAirqualityd.main(sys.argv[1:])
