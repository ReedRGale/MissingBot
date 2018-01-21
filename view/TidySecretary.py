# ----------- Script by ReedRGale ----------- #
# View object to simplify logging and retrieving data. #

import json
import os
from model import st


class TidySecretary:
    """Class designed to handle logging and retrieving TidyMessage data."""

    @staticmethod
    async def retrieve(path, whole=False):
        """Retrieve the last created page--if _all is True, return the whole file."""
        # Get the data for the file.
        open(path, "a").close()
        with open(path, "r") as fin:
            m_json = json.load(fin) if os.stat(path).st_size > 0 else {}
        return m_json[str((max(m_json, key=int)))] if not whole else m_json

    @staticmethod
    async def store(tm, prompt=False):
        """Store the TidyMessage in its proper place. If it needs a page, generates one."""
        # Retrieve the json.
        all_m_json = await TidySecretary.retrieve(tm.path, whole=True)

        # If no page, assign the correct page.
        if not tm.page:
            # If entry exists, give the TidyMessage the biggest page number++, otherwise, assign the first page.
            page = str(int(max(all_m_json, key=int)) + 1) if all_m_json else '0'

        # Convert TidyMessage to json, then add it to all the other entries.
        m_json = {st.FLD_CNTT: tm.message.embeds[0].description if not prompt else tm.prompt.content,
                  st.FLD_TTLE: tm.title,
                  st.FLD_MODE: tm.mode,
                  st.FLD_PAGE: page,
                  st.FLD_PATH: tm.path,
                  st.FLD_EDTBL: tm.editable}
        all_m_json[page] = m_json

        # Send the data to the proper location.
        with open(tm.path, "w") as fout:
            json.dump(all_m_json, fout, indent=1)
